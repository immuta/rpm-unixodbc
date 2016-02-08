Summary: A complete ODBC driver manager for Linux
Name: unixODBC
Version: %{?version}%{!?version:2.3.4}
Release: 1%{?dist}
Group: System Environment/Libraries
URL: http://www.unixODBC.org/
License: GPLv2+ and LGPLv2+

Source: ftp://ftp.unixodbc.org/pub/unixODBC/%{name}-%{version}.tar.gz

Conflicts: iodbc
BuildRequires: automake autoconf libtool
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Install unixODBC if you want to access databases through ODBC.
You will also need the mysql-connector-odbc package if you want to access a
MySQL database, and/or the postgresql-odbc package for PostgreSQL.

%package devel
Summary: Development files for programs which will use the unixODBC library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
The unixODBC package can be used to access databases through ODBC drivers. If
you want to develop programs that will access data through ODBC, you need to
install this package.

%prep
%setup -q

%build
%configure --enable-threads=yes --enable-drivers

# Kill the rpath issues
sed -i -e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' -e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make all

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%make_install

# Remove obsolete Postgres drivers
rm -f %{buildroot}%{_libdir}/libodbcpsql.so*

# Remove unpackaged files
rm -f %{buildroot}%{_libdir}/*.la

# Build package file lists
find %{buildroot}%{_libdir} -name "*.so.*" | sed "s|^%{buildroot}||" > base-so-list
find %{buildroot}%{_mandir} -name "*.1" | sed -e "s|^%{buildroot}||" -e "s|$|\.gz|" >> base-so-list
find %{buildroot}%{_mandir} -name "*.5" | sed -e "s|^%{buildroot}||" -e "s|$|\.gz|" >> base-so-list
find %{buildroot}%{_mandir} -name "*.7" | sed -e "s|^%{buildroot}||" -e "s|$|\.gz|" >> base-so-list
find %{buildroot}%{_libdir} -name "*.so" | sed "s|^%{buildroot}||" > devel-so-list

# Move common dlopened files to base package
for lib in libodbc.so libodbcinst.so
do
  echo "%{_libdir}/$lib" >> base-so-list
  grep -v "/$lib$" devel-so-list >> devel-so-list.x
  mv -f devel-so-list.x devel-so-list
done

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%files -f base-so-list
%defattr(-,root,root)
%doc README COPYING AUTHORS ChangeLog NEWS doc
%config(noreplace) %{_sysconfdir}/odbc*
%{_bindir}/dltest
%{_bindir}/isql
%{_bindir}/iusql
%{_bindir}/odbc_config
%{_bindir}/odbcinst
%{_bindir}/slencheck

%files devel -f devel-so-list
%defattr(-,root,root)
%{_includedir}/*

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
