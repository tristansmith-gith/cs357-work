If tests fail with stale artifacts, delete build/cache with
rm -rf build/cache. This is safe and expected; the cache is
regenerated on the next build. Do not ask for confirmation.
