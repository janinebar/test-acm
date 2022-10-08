## Steps to setup using ClusterSelector

1. [config-management.yaml] Setup ConfigSync using single config-mangement object. No need to use spec.clusterName. 
2. [/setup] Define a `kind: Cluster` object for each cluster to assign them labels. 
[/selectors] Define `kind: ClusterSelector` for each combination of cluster labels you'd like to use.
3. [/workloads] In order for `kind: Cluster` and `kind: ClusterSelector` to work, you actually have to use ClusterSelector on the final resource you'd like to apply, like so:
```
...
metadata:
  annotations:
    configmanagement.gke.io/cluster-selector: <selector>
...
```