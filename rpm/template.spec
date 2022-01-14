%bcond_without tests
%bcond_without weak_deps

%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%global __provides_exclude_from ^/opt/ros/rolling/.*$
%global __requires_exclude_from ^/opt/ros/rolling/.*$

Name:           ros-rolling-ament-clang-format
Version:        0.11.4
Release:        1%{?dist}%{?release_suffix}
Summary:        ROS ament_clang_format package

License:        Apache License 2.0
Source0:        %{name}-%{version}.tar.gz

Requires:       clang
Requires:       python%{python3_pkgversion}-PyYAML
Requires:       ros-rolling-ros-workspace
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  ros-rolling-ament-copyright
BuildRequires:  ros-rolling-ament-flake8
BuildRequires:  ros-rolling-ament-pep257
BuildRequires:  ros-rolling-ros-workspace
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{name}-doc = %{version}-%{release}
Provides:       %{name}-runtime = %{version}-%{release}

%description
The ability to check code against style conventions using clang-format and
generate xUnit test result files.

%prep
%autosetup -p1

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/rolling/setup.sh" ]; then . "/opt/ros/rolling/setup.sh"; fi
%py3_build

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/rolling/setup.sh" ]; then . "/opt/ros/rolling/setup.sh"; fi
%py3_install -- --prefix "/opt/ros/rolling"

%if 0%{?with_tests}
%check
# Look for a directory with a name indicating that it contains tests
TEST_TARGET=$(ls -d * | grep -m1 "\(test\|tests\)" ||:)
if [ -n "$TEST_TARGET" ] && %__python3 -m pytest --version; then
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/rolling/setup.sh" ]; then . "/opt/ros/rolling/setup.sh"; fi
%__python3 -m pytest $TEST_TARGET || echo "RPM TESTS FAILED"
else echo "RPM TESTS SKIPPED"; fi
%endif

%files
/opt/ros/rolling

%changelog
* Fri Jan 14 2022 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.11.4-1
- Autogenerated by Bloom

* Fri Dec 10 2021 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.11.3-1
- Autogenerated by Bloom

* Fri Jun 18 2021 Audrow Nash <audrow@openrobotics.org> - 0.11.2-1
- Autogenerated by Bloom

* Fri Jun 18 2021 Audrow Nash <audrow@openrobotics.org> - 0.11.0-1
- Autogenerated by Bloom

* Thu May 06 2021 Audrow Nash <audrow@openrobotics.org> - 0.10.6-1
- Autogenerated by Bloom

* Wed Apr 14 2021 Audrow Nash <audrow@openrobotics.org> - 0.10.5-1
- Autogenerated by Bloom

* Thu Mar 18 2021 Claire Wang <clairewang@openrobotics.org> - 0.10.4-1
- Autogenerated by Bloom

* Mon Mar 08 2021 Claire Wang <clairewang@openrobotics.org> - 0.10.3-3
- Autogenerated by Bloom

