# Copyright 2015 Open Source Robotics Foundation, Inc.
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

# to add more licenses do not extend this file
# instead create a separate package and register custom licenses as entry points

from collections import namedtuple
import os

LicenseEntryPoint = namedtuple(
    'LicenseEntryPoint', ['name', 'file_header', 'license_file', 'contributing_file'])

TEMPLATE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'template')


def read_license_data(path, name, prefix):
    path_template = os.path.join(path, prefix + '_%s.txt')

    with open(path_template % 'header', 'r') as h:
        file_header = h.read()
    with open(path_template % 'license', 'r') as h:
        license_file = h.read()
    with open(path_template % 'contributing', 'r') as h:
        contributing_file = h.read()

    return LicenseEntryPoint(name, file_header, license_file, contributing_file)


apache2 = read_license_data(TEMPLATE_DIRECTORY, 'Apache License, Version 2.0', 'apache2')
bsd2 = read_license_data(TEMPLATE_DIRECTORY, 'BSD License 2.0', 'bsd2')
mit = read_license_data(TEMPLATE_DIRECTORY, 'MIT License', 'mit')
