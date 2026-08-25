#!/usr/bin/env bash
set -Eeuo pipefail

###############################################################################
# WHIZARD 3.1.8 MPI/OpenMP reproducibility snapshot
#
# Purpose:
#   - preserve the exact installed binary tree
#   - preserve the exact CERN LCG source archive
#   - preserve build/install logs
#   - record toolchain and runtime provenance
#
# Snapshots are immutable/versioned. Nothing is overwritten except LATEST.
###############################################################################

export REPO="${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}"

export INSTALL_ROOT="${INSTALL_ROOT:-$REPO/local/whizard-3.1.8-mpi-omp}"
export LOG_ROOT="${LOG_ROOT:-$REPO/build_logs/whizard-3.1.8-mpi-omp}"

export SOURCE_TARBALL="${SOURCE_TARBALL:-/eos/user/c/cglenn/FCCWork/whizard/packages/whizard-3.1.8-cern-lcg-source.tar.gz}"

export EOS_REPRO_ROOT="${EOS_REPRO_ROOT:-/eos/user/c/cglenn/FCCWork/whizard/packages/whizard-3.1.8-mpi-omp-repro}"

export BASE_ENV="${BASE_ENV:-$REPO/environments/setup_lcg_devkey_head_fri_ttsp.sh}"

EXPECTED_SOURCE_SHA256="96bfdf2ec4476ab7945e50550a3294634af6bc0f472cf7848b5903887629ce55"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SNAPSHOT_TAG="${SNAPSHOT_TAG:-${STAMP}_build_success}"

SNAPSHOT="$EOS_REPRO_ROOT/$SNAPSHOT_TAG"

SOURCE_OUT="$SNAPSHOT/source"
INSTALL_OUT="$SNAPSHOT/install"
PROV_OUT="$SNAPSHOT/provenance"
LOG_OUT="$SNAPSHOT/logs"

###############################################################################
# Gate inputs.
###############################################################################

echo "================================================================"
echo "VALIDATE CURRENT INSTALL"
echo "================================================================"

test -d "$INSTALL_ROOT"
test -x "$INSTALL_ROOT/bin/whizard"
test -s "$SOURCE_TARBALL"
test -s "$BASE_ENV"

ACTUAL_SOURCE_SHA256="$(sha256sum "$SOURCE_TARBALL" | awk '{print $1}')"

echo "source=$SOURCE_TARBALL"
echo "source_sha256=$ACTUAL_SOURCE_SHA256"

if [[ "$ACTUAL_SOURCE_SHA256" != "$EXPECTED_SOURCE_SHA256" ]]; then
    echo "ERROR: source tarball SHA256 does not match frozen WHIZARD source." >&2
    exit 1
fi

if [[ -e "$SNAPSHOT" ]]; then
    echo "ERROR: snapshot already exists:" >&2
    echo "  $SNAPSHOT" >&2
    exit 1
fi

mkdir -p \
    "$SOURCE_OUT" \
    "$INSTALL_OUT" \
    "$PROV_OUT" \
    "$LOG_OUT"

###############################################################################
# Load build/runtime environment for provenance commands.
###############################################################################

source "$BASE_ENV"

export OCAML_ROOT=/cvmfs/sft.cern.ch/lcg/releases/ocaml/4.14.2-7a890/x86_64-el9-gcc14-opt
export PATH="$OCAML_ROOT/bin:$INSTALL_ROOT/bin:$PATH"
export LD_LIBRARY_PATH="$INSTALL_ROOT/lib:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1

hash -r

###############################################################################
# Preserve source archive.
###############################################################################

echo
echo "================================================================"
echo "PRESERVE SOURCE"
echo "================================================================"

cp -a \
    "$SOURCE_TARBALL" \
    "$SOURCE_OUT/whizard-3.1.8-cern-lcg-source.tar.gz"

sha256sum \
    "$SOURCE_OUT/whizard-3.1.8-cern-lcg-source.tar.gz" \
    > "$SOURCE_OUT/SHA256SUMS"

###############################################################################
# Preserve installed prefix exactly.
###############################################################################

echo
echo "================================================================"
echo "ARCHIVE INSTALLED PREFIX"
echo "================================================================"

INSTALL_PARENT="$(dirname "$INSTALL_ROOT")"
INSTALL_NAME="$(basename "$INSTALL_ROOT")"

INSTALL_ARCHIVE="$INSTALL_OUT/${INSTALL_NAME}.tar.gz"

tar \
    -C "$INSTALL_PARENT" \
    -czf "$INSTALL_ARCHIVE" \
    "$INSTALL_NAME"

sha256sum "$INSTALL_ARCHIVE" \
    > "$INSTALL_OUT/SHA256SUMS"

###############################################################################
# Record file-level checksums and symlinks.
###############################################################################

echo
echo "================================================================"
echo "INSTALL MANIFEST"
echo "================================================================"

(
    cd "$INSTALL_ROOT"

    find . \
        -type f \
        -print0 \
        | LC_ALL=C sort -z \
        | xargs -0 sha256sum
) > "$INSTALL_OUT/file_sha256_manifest.txt"

(
    cd "$INSTALL_ROOT"

    find . \
        -type l \
        -printf '%p -> %l\n' \
        | LC_ALL=C sort
) > "$INSTALL_OUT/symlink_manifest.txt"

(
    cd "$INSTALL_ROOT"

    find . \
        -printf '%y %p\n' \
        | LC_ALL=C sort
) > "$INSTALL_OUT/tree_manifest.txt"

###############################################################################
# Save the environment/setup script itself.
###############################################################################

cp -a \
    "$BASE_ENV" \
    "$PROV_OUT/$(basename "$BASE_ENV")"

sha256sum "$BASE_ENV" \
    > "$PROV_OUT/base_environment_sha256.txt"

###############################################################################
# General provenance.
###############################################################################

{
    echo "snapshot_tag=$SNAPSHOT_TAG"
    echo "snapshot_created_utc=$(date -u --iso-8601=seconds)"
    echo
    echo "repo=$REPO"
    echo "install_root=$INSTALL_ROOT"
    echo "source_tarball=$SOURCE_TARBALL"
    echo "source_sha256=$ACTUAL_SOURCE_SHA256"
    echo "base_environment=$BASE_ENV"
    echo
    echo "hostname=$(hostname)"
    echo "uname=$(uname -a)"
    echo
    echo "configure_flags:"
    echo "  --prefix=<INSTALL_ROOT>"
    echo "  --enable-fc-mpi"
    echo "  --with-mpi-lib=openmpi"
    echo "  --enable-fc-openmp"
    echo "  --disable-dependency-tracking"
    echo
    echo "FC=mpifort"
    echo "F77=mpifort"
    echo "TIRPC_CFLAGS=-I/usr/include/tirpc"
    echo "TIRPC_LIBS=-ltirpc"
    echo "OMP_NUM_THREADS=1"
    echo
    echo "build_parallelism=make -j8"
    echo
    echo "known_link_compatibility:"
    echo "  local libudev.so linker-name shim"
    echo "  runtime target supplied by EL9 libudev.so.1"
} > "$PROV_OUT/build_recipe.txt"

###############################################################################
# Tool versions and resolved paths.
###############################################################################

{
    echo "================================================================"
    echo "COMMAND PATHS"
    echo "================================================================"

    for cmd in \
        gcc g++ gfortran \
        mpifort mpirun \
        make \
        ocamlc ocamlopt \
        root-config HepMC3-config \
        whizard
    do
        printf '%-20s ' "$cmd"
        command -v "$cmd" 2>/dev/null || echo "NOT_FOUND"
    done

    echo
    echo "================================================================"
    echo "VERSIONS"
    echo "================================================================"

    gcc --version 2>/dev/null | sed -n '1p' || true
    g++ --version 2>/dev/null | sed -n '1p' || true
    gfortran --version 2>/dev/null | sed -n '1p' || true

    echo
    mpifort --version 2>/dev/null | sed -n '1p' || true

    echo
    mpirun --version 2>/dev/null | sed -n '1,3p' || true

    echo
    echo "ocamlc=$(ocamlc -version 2>/dev/null || true)"
    echo "ocamlopt=$(ocamlopt -version 2>/dev/null || true)"

    echo
    echo "ROOT=$(root-config --version 2>/dev/null || true)"
    echo "HepMC3=$(HepMC3-config --version 2>/dev/null || true)"

    echo
    "$INSTALL_ROOT/bin/whizard" --version 2>&1 || true

    echo
    echo "================================================================"
    echo "MPI WRAPPER"
    echo "================================================================"

    mpifort --showme:command 2>/dev/null || true
    mpifort --showme:compile 2>/dev/null || true
    mpifort --showme:link 2>/dev/null || true

} > "$PROV_OUT/toolchain.txt" 2>&1

###############################################################################
# Relevant environment variables.
###############################################################################

env \
    | LC_ALL=C sort \
    > "$PROV_OUT/environment_full.txt"

{
    env \
        | grep -E \
            '^(PATH|LD_LIBRARY_PATH|LIBRARY_PATH|CPATH|CPLUS_INCLUDE_PATH|C_INCLUDE_PATH|PKG_CONFIG_PATH|CMAKE_PREFIX_PATH|ROOTSYS|PYTHONPATH|FC|F77|CC|CXX|OMP_)=' \
        | LC_ALL=C sort
} > "$PROV_OUT/environment_relevant.txt" || true

###############################################################################
# Runtime dependency closure.
###############################################################################

ldd "$INSTALL_ROOT/bin/whizard" \
    > "$PROV_OUT/ldd_whizard.txt" 2>&1 || true

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
        > "$PROV_OUT/ldd_libwhizard.txt" 2>&1 || true

    readelf -d "$LIBWHIZARD" \
        > "$PROV_OUT/readelf_libwhizard_dynamic.txt" 2>&1 || true
fi

readelf -d "$INSTALL_ROOT/bin/whizard" \
    > "$PROV_OUT/readelf_whizard_dynamic.txt" 2>&1 || true

###############################################################################
# Preserve build logs/configuration evidence.
###############################################################################

if [[ -d "$LOG_ROOT" ]]; then
    tar \
        -C "$(dirname "$LOG_ROOT")" \
        -czf "$LOG_OUT/build_logs.tar.gz" \
        "$(basename "$LOG_ROOT")"

    sha256sum "$LOG_OUT/build_logs.tar.gz" \
        > "$LOG_OUT/SHA256SUMS"
fi

###############################################################################
# Copy reproducibility scripts into snapshot.
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$SNAPSHOT/scripts"

cp -a \
    "$SCRIPT_DIR"/*.sh \
    "$SNAPSHOT/scripts/" \
    2>/dev/null || true

###############################################################################
# Global snapshot checksum manifest.
###############################################################################

(
    cd "$SNAPSHOT"

    find . \
        -type f \
        ! -name 'SNAPSHOT_SHA256SUMS' \
        -print0 \
        | LC_ALL=C sort -z \
        | xargs -0 sha256sum
) > "$SNAPSHOT/SNAPSHOT_SHA256SUMS"

###############################################################################
# Update LATEST.
###############################################################################

printf '%s\n' "$SNAPSHOT_TAG" \
    > "$EOS_REPRO_ROOT/LATEST"

echo
echo "================================================================"
echo "SNAPSHOT COMPLETE"
echo "================================================================"

echo "SNAPSHOT=$SNAPSHOT"
echo "LATEST=$(cat "$EOS_REPRO_ROOT/LATEST")"
echo
echo "SNAPSHOT_FREEZE=PASS"
