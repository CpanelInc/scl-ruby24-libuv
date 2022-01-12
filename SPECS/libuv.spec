# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel
%global pkg ruby24

# Force Software Collections on
%global _scl_prefix %{ns_dir}
%global scl %{ns_name}-%{pkg}
# HACK: OBS Doesn't support macros in BuildRequires statements, so we have
#       to hard-code it here.
# https://en.opensuse.org/openSUSE:Specfile_guidelines#BuildRequires
%global scl_prefix %{scl}-
%{?scl:%scl_package libuv}
%{!?scl:%global pkg_name %{name}}
%global somajor 1

# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define release_prefix 2

Name: %{?scl_prefix}libuv
Epoch:   1
Version: 1.11.0
Release: %{release_prefix}%{?dist}.cpanel
Summary: Platform layer for Node.js
# the licensing breakdown is described in detail in the LICENSE file
License: MIT and BSD and ISC

BuildRequires: python
BuildRequires: scl-utils
BuildRequires: scl-utils-build
%{?scl:Requires:%scl_runtime}
%{?scl:BuildRequires: %{scl}-runtime}

URL: http://libuv.org/
Source0: http://dist.libuv.org/dist/v%{version}/libuv-v%{version}.tar.gz
Source1: gyp.tar.gz
Source2: libuv.pc.in
Patch0:  soname.patch

%{?scl:BuildRequires: %{?scl}-runtime}

Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
libuv is a new platform layer for Node. Its purpose is to abstract IOCP on
Windows and libev on Unix systems. We intend to eventually contain all platform
differences in this library.

%package devel
Summary: Development libraries for libuv
Group: Development/Libraries
Requires: %{?scl_prefix}%{pkg_name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: pkgconfig
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description devel
Development libraries for libuv

%prep
%setup -q -n %{pkg_name}-v%{version}
%patch0 -p0
tar -xzf %{SOURCE1}

%build

%{?scl:scl enable %{scl} "}
export CFLAGS='%{optflags}'
export CXXFLAGS='%{optflags}'
%{__python} ./gyp_uv.py -f make -Dcomponent=shared_library -Duv_library=shared_library -Dsoname_version=%{?scl:%{scl_name}-}%{version} --depth=`pwd`
BUILDTYPE=Release make %{?_smp_mflags} -C out 
%{?scl: "}

%install
#%{?scl:scl enable %{scl} - << \EOF}
#make DESTDIR=%{buildroot} install
#%{?scl:EOF}
#rm -f %{buildroot}%{_libdir}/libuv-nodejs.la

rm -rf %{buildroot}

install -d %{buildroot}%{_includedir}
install -d %{buildroot}%{_libdir}

install -pm644 include/uv.h %{buildroot}%{_includedir}

install out/Release/lib.target/libuv.so.%{?scl:%{scl_name}-}%{version} %{buildroot}%{_libdir}/libuv.so.%{?scl:%{scl_name}-}%{version}
ln -sf libuv.so.%{?scl:%{scl_name}-}%{version} %{buildroot}%{_libdir}/libuv.so.%{somajor}
ln -sf libuv.so.%{?scl:%{scl_name}-}%{version} %{buildroot}%{_libdir}/libuv.so

# Copy the headers into the include path
mkdir -p %{buildroot}/%{_includedir}/uv-private

cp include/uv.h \
   %{buildroot}/%{_includedir}

cp include/tree.h \
   %{buildroot}/%{_includedir}/uv-private
cp \
   include/uv-linux.h \
   include/uv-unix.h \
   include/uv-errno.h \
   include/uv-version.h \
   include/uv-threadpool.h \
   %{buildroot}/%{_includedir}/

# Create the pkgconfig file
mkdir -p %{buildroot}/%{_libdir}/pkgconfig

sed -e "s#@prefix@#%{_prefix}#g" \
    -e "s#@exec_prefix@#%{_exec_prefix}#g" \
    -e "s#@libdir@#%{_libdir}#g" \
    -e "s#@includedir@#%{_includedir}#g" \
    -e "s#@version@#%{version}#g" \
    %SOURCE2 > %{buildroot}/%{_libdir}/pkgconfig/libuv.pc

%check
# Tests are currently disabled because some require network access
# Working with upstream to split these out
#./out/Release/run-tests
#./out/Release/run-benchmarks

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc README.md AUTHORS LICENSE
%{_libdir}/libuv.so.*

%files devel
%doc README.md AUTHORS LICENSE
%{_libdir}/libuv.so
%{_libdir}/pkgconfig/libuv.pc
%{_includedir}/uv*.h
%{_includedir}/uv-private

%changelog
* Tue Dec 28 2021 Dan Muey <dan@cpanel.net> - 1.11.0-2
- ZC-9589: Update DISABLE_BUILD to match OBS

* Thu Apr 13 2017 Rishwanth Yeddula <rish@cpanel.net> - 4.24-1
- Initial package of libuv for the ea-ruby24 SCL

