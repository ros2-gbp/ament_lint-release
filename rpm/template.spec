%bcond_without tests
%bcond_without weak_deps

%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%global __provides_exclude_from ^/opt/ros/rolling/.*$
%global __requires_exclude_from ^/opt/ros/rolling/.*$

Name:           ros-rolling-ament-cmake-copyright
Version:        0.19.1
Release:        1%{?dist}%{?release_suffix}
Summary:        ROS ament_cmake_copyright package

License:        Apache License 2.0
Source0:        %{name}-%{version}.tar.gz

Requires:       ros-rolling-ament-cmake-test
Requires:       ros-rolling-ament-copyright
Requires:       ros-rolling-ros-workspace
BuildRequires:  ros-rolling-ament-cmake-core
BuildRequires:  ros-rolling-ament-cmake-test
BuildRequires:  ros-rolling-ament-copyright
BuildRequires:  ros-rolling-ros-workspace
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{name}-doc = %{version}-%{release}
Provides:       %{name}-runtime = %{version}-%{release}

%if 0%{?with_tests}
BuildRequires:  ros-rolling-ament-cmake-lint-cmake
%endif

%description
The CMake API for ament_copyright to check every source file contains copyright
reference.

%prep
%autosetup -p1

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/rolling/setup.sh" ]; then . "/opt/ros/rolling/setup.sh"; fi
mkdir -p .obj-%{_target_platform} && cd .obj-%{_target_platform}
%cmake3 \
    -UINCLUDE_INSTALL_DIR \
    -ULIB_INSTALL_DIR \
    -USYSCONF_INSTALL_DIR \
    -USHARE_INSTALL_PREFIX \
    -ULIB_SUFFIX \
    -DCMAKE_INSTALL_PREFIX="/opt/ros/rolling" \
    -DAMENT_PREFIX_PATH="/opt/ros/rolling" \
    -DCMAKE_PREFIX_PATH="/opt/ros/rolling" \
    -DSETUPTOOLS_DEB_LAYOUT=OFF \
%if !0%{?with_tests}
    -DBUILD_TESTING=OFF \
%endif
    ..

%make_build

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/rolling/setup.sh" ]; then . "/opt/ros/rolling/setup.sh"; fi
%make_install -C .obj-%{_target_platform}

%if 0%{?with_tests}
%check
# Look for a Makefile target with a name indicating that it runs tests
TEST_TARGET=$(%__make -qp -C .obj-%{_target_platform} | sed "s/^\(test\|check\):.*/\\1/;t f;d;:f;q0")
if [ -n "$TEST_TARGET" ]; then
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/rolling/setup.sh" ]; then . "/opt/ros/rolling/setup.sh"; fi
CTEST_OUTPUT_ON_FAILURE=1 \
    %make_build -C .obj-%{_target_platform} $TEST_TARGET || echo "RPM TESTS FAILED"
else echo "RPM TESTS SKIPPED"; fi
%endif

%files
/opt/ros/rolling

%changelog
* Sun Feb 02 2025 Chris Lalancette <clalancette@gmail.com> - 0.19.1-1
- Autogenerated by Bloom

* Wed Nov 20 2024 Chris Lalancette <clalancette@gmail.com> - 0.19.0-1
- Autogenerated by Bloom

* Mon Jun 17 2024 Chris Lalancette <clalancette@gmail.com> - 0.18.1-1
- Autogenerated by Bloom

* Fri Apr 26 2024 Chris Lalancette <clalancette@gmail.com> - 0.18.0-1
- Autogenerated by Bloom

* Tue Apr 16 2024 Chris Lalancette <clalancette@gmail.com> - 0.17.0-1
- Autogenerated by Bloom

* Thu Mar 28 2024 Chris Lalancette <clalancette@gmail.com> - 0.16.4-1
- Autogenerated by Bloom

* Tue Mar 05 2024 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.16.3-2
- Autogenerated by Bloom

