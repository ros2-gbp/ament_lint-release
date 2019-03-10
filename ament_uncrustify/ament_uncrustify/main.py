#!/usr/bin/env python3

# Copyright 2014-2015 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from configparser import ConfigParser
import difflib
import filecmp
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr


def main(argv=sys.argv[1:]):
    config_file = os.path.join(
        os.path.dirname(__file__),
        'configuration', 'ament_code_style.cfg')

    extensions = ['c', 'cc', 'cpp', 'cxx', 'h', 'hh', 'hpp', 'hxx']

    parser = argparse.ArgumentParser(
        description='Check code style using uncrustify.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-c',
        metavar='CFG',
        default=config_file,
        dest='config_file',
        help='The config file')
    parser.add_argument(
        '--linelength', metavar='N', type=int,
        help='The maximum line length (default: specified in the config file)')
    parser.add_argument(
        'paths',
        nargs='*',
        default=[os.curdir],
        help='The files or directories to check. For directories files ending '
             'in %s will be considered.' %
             ', '.join(["'.%s'" % e for e in extensions]))
    parser.add_argument(
        '--exclude',
        nargs='*',
        default=[],
        help='Exclude specific file names and directory names from the check')
    parser.add_argument(
        '--reformat',
        action='store_true',
        help='Reformat the files in place')
    # not using a file handle directly
    # in order to prevent leaving an empty file when something fails early
    parser.add_argument(
        '--xunit-file',
        help='Generate a xunit compliant XML file')
    args = parser.parse_args(argv)

    if not os.path.exists(args.config_file):
        print("Could not config file '%s'" % args.config_file, file=sys.stderr)
        return 1

    temp_config = None
    temp_path = None
    try:
        if args.linelength is not None:
            # check if different from config file
            config = ConfigParser()
            with open(args.config_file, 'r') as h:
                config_str = h.read()
            config.read_string('[DEFAULT]\n' + config_str)
            code_width = config['DEFAULT']['code_width']
            code_width = int(re.split('[ \t#]', code_width, maxsplit=1)[0])
            if args.linelength != code_width:
                # generate temporary config file with custom line length
                temp_config_fd, args.config_file = tempfile.mkstemp(prefix='uncrustify_')
                temp_config = os.fdopen(temp_config_fd, 'w')
                temp_config.write(config_str + '\ncode_width=%d' % args.linelength)
                temp_config.close()

        if args.xunit_file:
            start_time = time.time()

        files = get_files(args.paths, extensions, args.exclude)
        if not files:
            print('No files found', file=sys.stderr)
            return 1

        uncrustify_bin = find_executable('uncrustify')
        if not uncrustify_bin:
            print("Could not find 'uncrustify' executable", file=sys.stderr)
            return 1

        suffix = '.uncrustify'

        report = []
        temp_path = tempfile.mkdtemp(prefix='uncrustify_')

        # invoke uncrustify on all files
        input_files = [os.path.abspath(f) for f in files]

        # on Windows uncrustify fails to concatenate
        # the absolute prefix path with the absolute input files
        # https://github.com/bengardner/uncrustify/issues/364
        cwd = None
        if os.name == 'nt':
            cwd = os.path.commonprefix(input_files)
            if not os.path.isdir(cwd):
                cwd = os.path.dirname(cwd)
                assert os.path.isdir(cwd), \
                    'Could not determine common prefix of input files'
            input_files = [os.path.relpath(f, start=cwd) for f in input_files]

        try:
            cmd = [uncrustify_bin,
                   '-c', args.config_file,
                   '--prefix', temp_path,
                   '--suffix', suffix]
            cmd.extend(input_files)
            subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if e.output:
                print(e.output.decode(), file=sys.stderr)
            print("The invocation of 'uncrustify' failed with error code %d: %s" %
                  (e.returncode, e), file=sys.stderr)
            return 1

        if cwd:
            # input files are relative
            # prepend temp path, append suffix
            output_files = [
                os.path.join(temp_path, f + suffix) for f in input_files]
        else:
            # input files are absolute
            # remove leading slash, prepend temp path, append suffix
            output_files = [
                os.path.join(
                    temp_path,
                    os.sep.join(f.split(os.sep)[1:]) +
                    suffix
                ) for f in input_files
            ]

        uncrustified_files = output_files
        i = 1
        while True:
            # identify files which have changed since the latest uncrustify run
            changed_files = []
            for input_filename, output_filename in zip(
                    input_files, uncrustified_files):
                if cwd and not os.path.isabs(input_filename):
                    input_filename = os.path.join(cwd, input_filename)
                if not filecmp.cmp(input_filename, output_filename):
                    if output_filename == input_filename + suffix:
                        # for repeated invocations
                        # replace the previous uncrustified file
                        os.rename(output_filename, input_filename)
                        changed_files.append(input_filename)
                    else:
                        # after first invocation remove suffix
                        # otherwise uncrustify behaves different
                        output_filename_without_suffix = \
                            output_filename[:-len(suffix)]
                        os.rename(
                            output_filename, output_filename_without_suffix)
                        changed_files.append(output_filename_without_suffix)
            if not changed_files:
                break
            # reinvoke uncrustify for previously changed files
            input_files = changed_files
            try:
                cmd = [uncrustify_bin,
                       '-c', args.config_file,
                       '--suffix', suffix]
                cmd.extend(input_files)
                subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                if e.output:
                    print(e.output, file=sys.stderr)
                print("The invocation of 'uncrustify' failed with error code %d: %s" %
                      (e.returncode, e), file=sys.stderr)
                return 1

            uncrustified_files = [f + suffix for f in input_files]
            i += 1
            if i >= 5:
                print("'uncrustify' did not settle on a final result even "
                      "after %d invocations" % i, file=sys.stderr)
                return 1

        # compute diff
        for index, filename in enumerate(files):
            modified_filename = output_files[index]
            with open(filename, 'r') as original_file:
                with open(modified_filename, 'r') as modified_file:
                    diff_lines = list(difflib.unified_diff(
                        original_file.readlines(), modified_file.readlines(),
                        fromfile=filename, tofile=filename + suffix,
                        n=0))
                    report.append((filename, diff_lines))
            if args.reformat:
                # overwrite original with reformatted file
                with(open(filename, 'wb')) as original_file:
                    with open(modified_filename, 'rb') as modified_file:
                        original_file.write(modified_file.read())
    finally:
        if temp_config:
            os.remove(args.config_file)
        if temp_path and os.path.exists(temp_path):
            shutil.rmtree(temp_path)

    # output diffs
    for (filename, diff_lines) in report:
        if diff_lines:
            if not args.reformat:
                print("Code style divergence in file '%s':" % filename,
                      file=sys.stderr)
                print('', file=sys.stderr)
                for line in diff_lines:
                    print(line.rstrip('\r\n'), file=sys.stderr)
                print('', file=sys.stderr)
            else:
                print("Code style divergence in file '%s': reformatted file" %
                      filename)
        else:
            print("No code style divergence in file '%s'" % filename)
            if not args.reformat:
                print('')

    # output summary
    error_count = sum([1 if r[1] else 0 for r in report])
    if not error_count:
        print('No errors')
        rc = 0
    else:
        print('%d files with code style divergence' % error_count,
              file=sys.stderr)
        rc = 1

    # generate xunit file
    if args.xunit_file:
        folder_name = os.path.basename(os.path.dirname(args.xunit_file))
        file_name = os.path.basename(args.xunit_file)
        suffix = '.xml'
        if file_name.endswith(suffix):
            file_name = file_name[0:-len(suffix)]
            suffix = '.xunit'
            if file_name.endswith(suffix):
                file_name = file_name[0:-len(suffix)]
        testname = '%s.%s' % (folder_name, file_name)

        xml = get_xunit_content(report, testname, time.time() - start_time)
        path = os.path.dirname(os.path.abspath(args.xunit_file))
        if not os.path.exists(path):
            os.makedirs(path)
        with open(args.xunit_file, 'w') as f:
            f.write(xml)

    return rc


def find_executable(file_name, additional_paths=None):
    path = None
    if additional_paths:
        path = os.getenv('PATH', os.defpath)
        path += os.path.pathsep + os.path.pathsep.join(additional_paths)
    return shutil.which(file_name, path=path)


def get_files(paths, extensions, excludes=[]):
    files = []
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                if 'AMENT_IGNORE' in filenames:
                    dirnames[:] = []
                    continue
                # ignore folder starting with . or _
                dirnames[:] = [d for d in dirnames if d[0] not in ['.', '_']]
                # ignore excluded folders
                dirnames[:] = [d for d in dirnames if d not in excludes]
                dirnames.sort()

                # select files by extension
                for filename in sorted(filenames):
                    if filename in excludes:
                        continue
                    _, ext = os.path.splitext(filename)
                    if ext not in ['.%s' % e for e in extensions]:
                        continue
                    files.append(os.path.join(dirpath, filename))
        if os.path.isfile(path):
            files.append(path)
    return [os.path.normpath(f) for f in files]


def get_xunit_content(report, testname, elapsed):
    test_count = len(report)
    error_count = sum([1 if r[1] else 0 for r in report])
    data = {
        'testname': testname,
        'test_count': test_count,
        'error_count': error_count,
        'time': '%.3f' % round(elapsed, 3),
    }
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite
  name="%(testname)s"
  tests="%(test_count)d"
  failures="%(error_count)d"
  time="%(time)s"
>
""" % data

    for (filename, diff_lines) in report:

        if diff_lines:
            # report any diff as a failing testcase
            data = {
                'quoted_location': quoteattr(filename),
                'testname': testname,
                'quoted_message': quoteattr(
                    'Diff with %d lines' % len(diff_lines)
                ),
                'cdata': ''.join(diff_lines),
            }
            xml += """  <testcase
    name=%(quoted_location)s
    classname="%(testname)s"
  >
      <failure message=%(quoted_message)s><![CDATA[%(cdata)s]]></failure>
  </testcase>
""" % data

        else:
            # if there is no diff report a single successful test
            data = {
                'quoted_location': quoteattr(filename),
                'testname': testname,
            }
            xml += """  <testcase
    name=%(quoted_location)s
    classname="%(testname)s"
    status="No errors"/>
""" % data

    # output list of checked files
    data = {
        'escaped_files': escape(''.join(['\n* %s' % r[0] for r in report])),
    }
    xml += """  <system-out>Checked files:%(escaped_files)s</system-out>
""" % data

    xml += '</testsuite>\n'
    return xml


if __name__ == '__main__':
    sys.exit(main())
