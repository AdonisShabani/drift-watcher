# drift-watcher
driftwatch is a Python library for detecting configuration drift across multi-stack infrastructure. The user defines what their services should look like (expected state), and the library compares that against live state from Kubernetes and GCP, then reports what drifted, when, and how severely.
