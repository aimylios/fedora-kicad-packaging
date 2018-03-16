#!/bin/sh

set -e
set -x

show_help () {
    set +x
    echo "$0 [-c COPR_ID] [-m MOCK_TARGET] [-h]" >&2
    echo "" >&2
    echo "  -h shows this help message." >&2
    echo "  -n PKG_NAME selects the package to build." >&2
    echo "  -c COPR_ID performs a remote COPR build using the specified ID." >&2
    echo "  -m MOCK_TARGET performs a local MOCK build for the specified target." >&2
    echo "" >&2
    echo "If neither -c nor -m is specified, then no build will be done, but" >&2
    echo "the SRPM will still be prepared, and can be used to manually kick off" >&2
    echo "a build at a later time." >&2
    echo "" >&2
    echo "example: $0 -c your_copr_id/kicad" >&2
    echo "example: $0 -m fedora-27-x86_64" >&2
    set -x
}

PKG_NAME="kicad"
COPR_ID=
MOCK_TARGET=
while getopts ":h:n:c:m:" opt; do
    case "$opt" in
        h)
            show_help
            exit 1
            ;;
        n)
            PKG_NAME="${OPTARG}"
            ;;
        c)
            COPR_ID="${OPTARG}"
            ;;
        m)
            MOCK_TARGET="${OPTARG}"
            ;;
        \?)
            set +x
            echo "Invalid option: -${OPTARG}" >&2
            set -x
            show_help
            exit 1
            ;;
        :)
            set +x
            echo "Option -${OPTARG} requires an argument." >&2
            set -x
            show_help
            exit 1
            ;;
    esac
done

set +x
echo "Generating SRPM..."
set -x
RPMBUILD=rpmbuild
rpmbuild --define "_topdir ${RPMBUILD}" -bs "${RPMBUILD}/SPECS/${PKG_NAME}.spec"

# Get the name of the SRPM file.  We have to fill in the "dist" field.
SRPM=$(find rpmbuild/SRPMS -name "${PKG_NAME}-r*.src.rpm")
set +x
echo "Prepared ${SRPM}..."
set -x

# Do a local mock build.
if [ -n "${MOCK_TARGET}" ]; then
    set +x
    echo "Starting the local mock build."
    set -x
    mock -r "${MOCK_TARGET}" --rebuild "${SRPM}"
fi

# Do a remote copr build.
if [ -n "${COPR_ID}" ]; then
    set +x
    STATUS_LOCATION=$(echo ${COPR_ID} | sed -e 's/@/g\//')
    echo "Starting the remote copr build. Check the status of the build here:"
    echo "https://copr.fedoraproject.org/coprs/${STATUS_LOCATION}/builds/"
    set -x
    copr-cli build "${COPR_ID}" "${SRPM}"
fi

exit 0
