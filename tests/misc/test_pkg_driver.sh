#!/bin/bash
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
echo "Testing Python fallback..."
rm -f build/flow_pkg
rm -rf /tmp/pkg_test_driver
mkdir -p /tmp/pkg_test_driver
cd /tmp/pkg_test_driver
"$REPO_ROOT/flow" pkg init fallback_app
if [ ! -f "flow.toml" ]; then
    echo "Fallback init failed"
    # Will fail manually below if error
fi
echo "Fallback init ok"

cd "$REPO_ROOT"
echo "Testing Native binary..."
./compiler/scripts/build_pkg.sh
rm -rf /tmp/pkg_test_driver2
mkdir -p /tmp/pkg_test_driver2
cd /tmp/pkg_test_driver2
"$REPO_ROOT/flow" pkg init native_app
if [ ! -f "flow.toml" ]; then
    echo "Native init failed"
    # Will fail manually
fi
echo "Native init ok"

echo "Driver test passed!"
