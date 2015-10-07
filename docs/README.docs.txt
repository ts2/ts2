The docs compilation is run from `fabric` as a script.

```
# goto root
cd ../

# Build docs
fab docs_build

# Run docs server default=8080
fab docs_server
```

Docs are output to `temp/build_docs `directory

Update online at with
- http://docs-ts2.rhcloud.com/
- with docs_update_www
- permissions required see npi or pedro




