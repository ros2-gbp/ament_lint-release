%bcond_without tests
%bcond_without weak_deps

%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%global __provides_exclude_from ^/opt/ros/humble/.*$
%global __requires_exclude_from ^/opt/ros/humble/.*$

Name:           ros-humble-ament-cmake-pclint
Version:        0.12.12
Release:        1%{?dist}%{?release_suffix}
Summary:        ROS ament_cmake_pclint package

License:        Apache License 2.0
Source0:        %{name}-%{version}.tar.gz

Requires:       ros-humble-ament-cmake-test
Requires:       ros-humble-ament-pclint
Requires:       ros-humble-ros-workspace
BuildRequires:  ros-humble-ament-cmake-core
BuildRequires:  ros-humble-ament-cmake-test
BuildRequires:  ros-humble-ros-workspace
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{name}-doc = %{version}-%{release}
Provides:       %{name}-runtime = %{version}-%{release}

%if 0%{?with_tests}
BuildRequires:  ros-humble-ament-cmake-copyright
BuildRequires:  ros-humble-ament-cmake-lint-cmake
%endif

%description
The CMake API for ament_pclint to perform static code analysis on C/C++ code
using PC-lint.

%prep
%autosetup -p1

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/humble/setup.sh" ]; then . "/opt/ros/humble/setup.sh"; fi
mkdir -p .obj-%{_target_platform} && cd .obj-%{_target_platform}
%cmake3 \
    -UINCLUDE_INSTALL_DIR \
    -ULIB_INSTALL_DIR \
    -USYSCONF_INSTALL_DIR \
    -USHARE_INSTALL_PREFIX \
    -ULIB_SUFFIX \
    -DCMAKE_INSTALL_PREFIX="/opt/ros/humble" \
    -DAMENT_PREFIX_PATH="/opt/ros/humble" \
    -DCMAKE_PREFIX_PATH="/opt/ros/humble" \
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
if [ -f "/opt/ros/humble/setup.sh" ]; then . "/opt/ros/humble/setup.sh"; fi
%make_install -C .obj-%{_target_platform}

%if 0%{?with_tests}
%check
# Look for a Makefile target with a name indicating that it runs tests
TEST_TARGET=$(%__make -qp -C .obj-%{_target_platform} | sed "s/^\(test\|check\):.*/\\1/;t f;d;:f;q0")
if [ -n "$TEST_TARGET" ]; then
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/humble/setup.sh" ]; then . "/opt/ros/humble/setup.sh"; fi
CTEST_OUTPUT_ON_FAILURE=1 \
    %make_build -C .obj-%{_target_platform} $TEST_TARGET || echo "RPM TESTS FAILED"
else echo "RPM TESTS SKIPPED"; fi
%endif

%files
/opt/ros/humble

%changelog
* Tue Mar 25 2025 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.12-1
- Autogenerated by Bloom

* Wed May 15 2024 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.11-1
- Autogenerated by Bloom

* Wed Jan 24 2024 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.10-1
- Autogenerated by Bloom

* Mon Nov 13 2023 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.9-1
- Autogenerated by Bloom

* Tue Sep 19 2023 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.8-1
- Autogenerated by Bloom

* Mon Jul 17 2023 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.7-2
- Autogenerated by Bloom

* Mon Jul 17 2023 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.7-1
- Autogenerated by Bloom

* Tue Apr 25 2023 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.6-1
- Autogenerated by Bloom

* Thu Jan 12 2023 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.5-1
- Autogenerated by Bloom

* Mon May 09 2022 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.4-1
- Autogenerated by Bloom

* Tue Apr 19 2022 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.3-2
- Autogenerated by Bloom

* Fri Apr 08 2022 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.3-1
- Autogenerated by Bloom

* Mon Mar 28 2022 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.2-1
- Autogenerated by Bloom

* Tue Mar 01 2022 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.1-1
- Autogenerated by Bloom

* Fri Feb 18 2022 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.12.0-1
- Autogenerated by Bloom

* Tue Feb 08 2022 Michael Jeronimo <michael.jeronimo@openrobotics.org> - 0.11.4-2
- Autogenerated by Bloom

