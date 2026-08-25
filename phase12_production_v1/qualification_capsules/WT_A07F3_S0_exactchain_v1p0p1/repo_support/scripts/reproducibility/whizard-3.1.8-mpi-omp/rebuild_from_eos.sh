#!/usr/bin/env bash
set -Eeuo pipefail

###############################################################################
# Rebuild WHIZARD 3.1.8 with MPI + OpenMP from the frozen CERN source archive.
#
# All important locations may be overridden from the environment.
#
# Example:
#
#   REPO=/path/to/repo \
#   INSTALL_ROOT=/path/to/install \
#   SOURCE_TARBALL=/path/to/frozen/source.tar.gz \
#   BASE_ENV=/path/to/setup.sh \
#   ./rebuild_from_eos.sh
###############################################################################

export REPO="${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}"

export SOURCE_TARBALL="${SOURCE_TARBALL:-/eos/user/c/cglenn/FCCWork/whizard/packages/whizard-3.1.8-cern-lcg-source.tar.gz}"

export INSTALL_ROOT="${INSTALL_ROOT:-$REPO/local/whizard-3.1.8-mpi-omp}"

export BASE_ENV="${BASE_ENV:-$REPO/environments/setup_lcg_devkey_head_fri_ttsp.sh}"

export BUILD_PARENT="${BUILD_PARENT:-/tmp/${USER}/whizard-3.1.8-mpi-omp-build}"
export BUILD_SOURCE="$BUILD_PARENT/whizard-3.1.8"

export LOG_ROOT="${LOG_ROOT:-$REPO/build_logs/whizard-3.1.8-mpi-omp-rebuild/$(date -u +%Y%m%dT%H%M%SZ)}"

export COMPAT_ROOT="${COMPAT_ROOT:-$REPO/local/el9-link-compat}"
export COMPAT_LIB="$COMPAT_ROOT/lib"

export JOBS="${JOBS:-8}"

EXPECTED_SOURCE_SHA256="96bfdf2ec4476ab7945e50550a3294634af6bc0f472cf7848b5903887629ce55"

###############################################################################
# Safety gates.
###############################################################################

test -s "$SOURCE_TARBALL"
test -s "$BASE_ENV"

ACTUAL_SOURCE_SHA256="$(sha256sum "$SOURCE_TARBALL" | awk '{print $1}')"

if [[ "$ACTUAL_SOURCE_SHA256" != "$EXPECTED_SOURCE_SHA256" ]]; then
    echo "ERROR: source archive SHA256 mismatch." >&2
    echo "expected=$EXPECTED_SOURCE_SHA256" >&2
    echo "actual=$ACTUAL_SOURCE_SHA256" >&2
    exit 1
fi

if [[ -e "$INSTALL_ROOT" ]]; then
    if [[ "${WHIZARD_REBUILD_ALLOW_OVERWRITE:-0}" != "1" ]]; then
        echo "ERROR: INSTALL_ROOT already exists:" >&2
        echo "  $INSTALL_ROOT" >&2
        echo >&2
        echo "Use a new INSTALL_ROOT, or explicitly set:" >&2
        echo "  WHIZARD_REBUILD_ALLOW_OVERWRITE=1" >&2
        exit 1
    fi

    rm -rf "$INSTALL_ROOT"
fi

mkdir -p \
    "$LOG_ROOT" \
    "$COMPAT_LIB"

###############################################################################
# Base LCG environment.
###############################################################################

source "$BASE_ENV"

export OCAML_ROOT=/cvmfs/sft.cern.ch/lcg/releases/ocaml/4.14.2-7a890/x86_64-el9-gcc14-opt
export PATH="$OCAML_ROOT/bin:$PATH"

export FC=mpifort
export F77=mpifort

export OMP_NUM_THREADS=1

export TIRPC_CFLAGS="-I/usr/include/tirpc"
export TIRPC_LIBS="-ltirpc"

hash -r

###############################################################################
# EL9/OpenMPI compatibility layer.
#
# Add future compatibility fixes ONLY in this section.
###############################################################################

echo "================================================================"
echo "SETUP LINK COMPATIBILITY"
echo "================================================================"

test -e /lib64/libudev.so.1

UDEV_REAL="$(readlink -f /lib64/libudev.so.1)"

test -e "$UDEV_REAL"

ln -sfn \
    "$UDEV_REAL" \
    "$COMPAT_LIB/libudev.so"

echo "libudev.so -> $UDEV_REAL"

###############################################################################
# Recreate source tree.
###############################################################################

echo
echo "================================================================"
echo "EXTRACT SOURCE"
echo "================================================================"

rm -rf "$BUILD_PARENT"
mkdir -p "$BUILD_PARENT"

tar \
    -xzf "$SOURCE_TARBALL" \
    -C "$BUILD_PARENT"

test -x "$BUILD_SOURCE/configure"
test -s "$BUILD_SOURCE/circe1/src/circe1.f90"

###############################################################################
# Provenance before build.
###############################################################################

{
    echo "date_utc=$(date -u --iso-8601=seconds)"
    echo "hostname=$(hostname)"
    echo "source=$SOURCE_TARBALL"
    echo "source_sha256=$ACTUAL_SOURCE_SHA256"
    echo "install_root=$INSTALL_ROOT"
    echo
    echo "FC=$(command -v mpifort)"
    echo "MPI_backend=$(mpifort --showme:command)"
    echo "MPI_version:"
    mpirun --version | sed -n '1,3p'
    echo
    echo "OCaml=$(ocamlc -version)"
    echo
    gcc --version | sed -n '1p'
    gfortran --version | sed -n '1p'
} > "$LOG_ROOT/prebuild_provenance.txt"

###############################################################################
# Configure.
###############################################################################

echo
echo "================================================================"
echo "CONFIGURE"
echo "================================================================"

cd "$BUILD_SOURCE"

set +e

FC=mpifort \
F77=mpifort \
TIRPC_CFLAGS="$TIRPC_CFLAGS" \
TIRPC_LIBS="$TIRPC_LIBS" \
./configure \
    --prefix="$INSTALL_ROOT" \
    --enable-fc-mpi \
    --with-mpi-lib=openmpi \
    --enable-fc-openmp \
    --disable-dependency-tracking \
    2>&1 \
    | tee "$LOG_ROOT/configure.log"

CONFIG_RC=${PIPESTATUS[0]}

set -e

if (( CONFIG_RC != 0 )); then
    echo "ERROR: configure failed: $CONFIG_RC" >&2
    exit "$CONFIG_RC"
fi

grep -E \
    'OpenMP:|MPI:|MPI Library:' \
    "$LOG_ROOT/configure.log" \
    > "$LOG_ROOT/configure_parallel_summary.txt" \
    || true

###############################################################################
# Build.
###############################################################################

echo
echo "================================================================"
echo "BUILD"
echo "================================================================"

set +e

make \
    -j"$JOBS" \
    LDFLAGS="-L$COMPAT_LIB" \
    2>&1 \
    | tee "$LOG_ROOT/build.log"

BUILD_RC=${PIPESTATUS[0]}

set -e

if (( BUILD_RC != 0 )); then
    echo "ERROR: build failed: $BUILD_RC" >&2
    exit "$BUILD_RC"
fi

###############################################################################
# Install.
###############################################################################

echo
echo "================================================================"
echo "INSTALL"
echo "================================================================"

set +e

make \
    LDFLAGS="-L$COMPAT_LIB" \
    install \
    2>&1 \
    | tee "$LOG_ROOT/install.log"

INSTALL_RC=${PIPESTATUS[0]}

set -e

if (( INSTALL_RC != 0 )); then
    echo "ERROR: install failed: $INSTALL_RC" >&2
    exit "$INSTALL_RC"
fi

###############################################################################
# Runtime setup.
###############################################################################

export PATH="$INSTALL_ROOT/bin:$PATH"
export LD_LIBRARY_PATH="$INSTALL_ROOT/lib:${LD_LIBRARY_PATH:-}"

hash -r

###############################################################################
# Validation.
###############################################################################

echo
echo "================================================================"
echo "VALIDATE INSTALL"
echo "================================================================"

test -x "$INSTALL_ROOT/bin/whizard"
test -s "$INSTALL_ROOT/lib/libwhizard.so"

"$INSTALL_ROOT/bin/whizard" --version \
    | tee "$LOG_ROOT/installed_version.txt"

echo
echo "================================================================"
echo "PARALLEL LINKAGE"
echo "================================================================"

ldd "$INSTALL_ROOT/bin/whizard" \
    > "$LOG_ROOT/ldd_whizard.txt"

LIBWHIZARD="$(
    find "$INSTALL_ROOT/lib" \
        -maxdepth 1 \
        -type f \
        -name 'libwhizard.so.*' \
        | LC_ALL=C sort \
        | sed -n '1p'
)"

if [[ -n "$LIBWHIZARD" ]]; then
    ldd "$LIBWHIZARD" \
        > "$LOG_ROOT/ldd_libwhizard.txt"
fi

###############################################################################
# Record final recipe.
###############################################################################

cat > "$INSTALL_ROOT/PARALLEL_BUILD_PROVENANCE.txt" <<EOF
WHIZARD_VERSION=3.1.8
BUILD_DATE_UTC=$(date -u --iso-8601=seconds)

SOURCE_TARBALL=$SOURCE_TARBALL
SOURCE_SHA256=$ACTUAL_SOURCE_SHA256

BASE_ENV=$BASE_ENV

FC=mpifort
F77=mpifort

TIRPC_CFLAGS=-I/usr/include/tirpc
TIRPC_LIBS=-ltirpc

CONFIGURE_FLAGS=
  --prefix=$INSTALL_ROOT
  --enable-fc-mpi
  --with-mpi-lib=openmpi
  --enable-fc-openmp
  --disable-dependency-tracking

BUILD_COMMAND=
  make -j$JOBS LDFLAGS=-L$COMPAT_LIB

INSTALL_COMMAND=
  make LDFLAGS=-L$COMPAT_LIB install

LINK_COMPAT_DIR=$COMPAT_LIB
LINK_COMPAT_LIBUDEV=$(readlink -f "$COMPAT_LIB/libudev.so")

LOG_ROOT=$LOG_ROOT
EOF

echo
echo "================================================================"
echo "REBUILD COMPLETE"
echo "================================================================"

echo "INSTALL_ROOT=$INSTALL_ROOT"
echo "LOG_ROOT=$LOG_ROOT"
echo
echo "WHIZARD_REBUILD=PASS"
