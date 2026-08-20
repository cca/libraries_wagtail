#!/bin/bash
# Force cleanup of libraries-wagtail namespace and all stuck resources
# Usage: ./cleanup-namespace.sh

NAMESPACE="libraries-wagtail"

echo "🧹 Cleaning up ${NAMESPACE} namespace and all resources..."

# Check if namespace exists
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "✓ Namespace exists, proceeding with cleanup..."
else
    echo "⚠ Namespace doesn't exist as an object, but resources may still be orphaned"
    echo "  Creating namespace to allow proper cleanup..."
    kubectl create namespace "$NAMESPACE" 2>/dev/null || true
fi

# Force delete all resources
echo "→ Deleting all workload resources..."
kubectl delete all --all -n "$NAMESPACE" --force --grace-period=0 2>/dev/null || true

echo "→ Deleting PVCs..."
kubectl delete pvc --all -n "$NAMESPACE" --force --grace-period=0 2>/dev/null || true

echo "→ Deleting configmaps and secrets..."
kubectl delete configmap,secret --all -n "$NAMESPACE" 2>/dev/null || true

# Wait a moment for deletions to process
sleep 2

# Patch any stuck PVCs to remove finalizers
echo "→ Removing finalizers from stuck PVCs..."
for pvc in $(kubectl get pvc -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null); do
    echo "  Patching PVC: $pvc"
    kubectl patch pvc "$pvc" -n "$NAMESPACE" -p '{"metadata":{"finalizers":null}}' --type=merge 2>/dev/null || true
done

# Patch any stuck PVs related to this namespace
echo "→ Removing finalizers from stuck PVs..."
for pv in $(kubectl get pv -o json | jq -r ".items[] | select(.spec.claimRef.namespace==\"$NAMESPACE\") | .metadata.name" 2>/dev/null); do
    echo "  Patching PV: $pv"
    kubectl patch pv "$pv" -p '{"metadata":{"finalizers":null}}' --type=merge 2>/dev/null || true
done

# Delete the namespace
echo "→ Deleting namespace..."
kubectl delete namespace "$NAMESPACE" 2>/dev/null || true

# Wait and verify
sleep 2

# Clean up any Released PVs
echo "→ Cleaning up Released PVs..."
for pv in $(kubectl get pv -o json | jq -r ".items[] | select(.status.phase==\"Released\" and .spec.claimRef.namespace==\"$NAMESPACE\") | .metadata.name" 2>/dev/null); do
    echo "  Deleting PV: $pv"
    kubectl delete pv "$pv" 2>/dev/null || true
done

# Final verification
echo ""
echo "🔍 Verification:"
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "⚠ Namespace still exists (may be terminating)"
else
    echo "✓ Namespace deleted"
fi

REMAINING_PVS=$(kubectl get pv -o json 2>/dev/null | jq -r ".items[] | select(.spec.claimRef.namespace==\"$NAMESPACE\") | .metadata.name" | wc -l)
if [ "$REMAINING_PVS" -eq 0 ]; then
    echo "✓ No PVs remaining for $NAMESPACE"
else
    echo "⚠ $REMAINING_PVS PV(s) still exist for $NAMESPACE"
fi

echo ""
echo "✅ Cleanup complete!"
