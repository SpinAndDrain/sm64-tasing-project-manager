import time
import os
import bson


KEY_LATEST_COMMIT_HASH = 'latest-commit-hash'
KEY_CACHE = 'cache'


class NormalIteratorThatEveryAverageProgrammingLanguageHas():
    def __init__(self, array):
        self._array = array
        self._ptr = 0
    
    def has_next(self):
        return self._ptr < len(self._array)
    
    def next(self):
        nxt = self._array[self._ptr]
        self._ptr += 1
        return nxt
    
    def peek(self):
        return self._array[self._ptr]
    
    def reset(self):
        self._ptr = 0


def _recursive_delete_branch(cdict, iterx, unused):
    nxt = iterx.next()
    if iterx.has_next():
        _recursive_delete_branch(cdict[nxt], iterx, unused)
        if len(cdict[nxt]) == 0:
            del cdict[nxt]
    else:
        del cdict[nxt]


def _recursive_add_branch(cdict, iterx, author):
    nxt = iterx.next()
    if not iterx.has_next():
        cdict[nxt] = author or 1
        return
    if nxt not in cdict:
        cdict[nxt] = {}
    _recursive_add_branch(cdict[nxt], iterx, author)


# remote file tree cache
class RftCache():
    def __init__(self, disc_cache_state_path, ghtraffic):
        self._disc_cache_state_path = disc_cache_state_path
        self._ghtraffic = ghtraffic
        self._cache = None
    
    def integrate(self):
        print("[Info] Integrating RFT cache...")

        if os.path.exists(self._disc_cache_state_path):
            with open(self._disc_cache_state_path, 'rb') as f:
                self._cache = bson.loads(f.read())

        latest_commit_hash = self._ghtraffic.get_latest_commit_hash()
        if not self._cache or not latest_commit_hash or self._cache[KEY_LATEST_COMMIT_HASH] != latest_commit_hash:
            print("[Info] Local RFT cache is desynchronized!")
            print("[Info] Synchronizing local RFT cache with remote repository (this may take a few minutes)...")

            api_request_count = 0
            elements_scanned_count = 0
            def _inc(id):
                if id == 0:
                    nonlocal api_request_count
                    api_request_count += 1
                elif id == 1:
                    nonlocal elements_scanned_count
                    elements_scanned_count += 1

            now = time.time()

            self._cache = {}
            self._cache[KEY_LATEST_COMMIT_HASH] = latest_commit_hash
            self._cache[KEY_CACHE] = {}
            self._recursive_synchronize(_inc, self._cache[KEY_CACHE])

            print(f"[Info] Synchronization complete. Took {(time.time() - now):.2f}s with {api_request_count} API requests. Total number of elements scanned: {elements_scanned_count}")
            self.write_to_disc()
        
        print("[Info] RFT cache integration complete")

    def write(self, path, commit_hash, delete = False, author = 1):
        self._cache[KEY_LATEST_COMMIT_HASH] = commit_hash
        it = NormalIteratorThatEveryAverageProgrammingLanguageHas(path.strip().split('/'))
        f = _recursive_delete_branch if delete else _recursive_add_branch
        f(self._cache[KEY_CACHE], it, author)
        self.write_to_disc()

    def write_to_disc(self):
        in_bson = bson.dumps(self._cache)
        with open(self._disc_cache_state_path, 'wb') as f:
            f.write(in_bson)

    def get_root(self):
        return self._cache[KEY_CACHE] if KEY_CACHE in self._cache else {}

    def get_element(self, path):
        current_dir = self.get_root()
        it = NormalIteratorThatEveryAverageProgrammingLanguageHas(path.strip().split('/'))
        while it.has_next():
            nxt = it.next()
            if not nxt:
                # ignore empty path segment
                continue
            if (not isinstance(current_dir, dict)) or (nxt not in current_dir):
                return None
            current_dir = current_dir[nxt]
        return current_dir

    def _recursive_synchronize(self, counter_function, cache_dict, path=''):
        counter_function(0)
        result = self._ghtraffic.get_element(path)
        if not result:
            return
        counter_function(1)
        for element in result:
            if element.type == "file":
                counter_function(0)
                author = self._ghtraffic.get_author(element.path)
                cache_dict[element.name] = author or 1
                if not author:
                    print(f"[Warning] Object has no author: {element.path} : {element.name}")
            elif element.type == "dir":
                cache_dict[element.name] = {}
                self._recursive_synchronize(counter_function, cache_dict[element.name], element.path)
            else:
                print(f"[Warning] Found invalid object while synchronizing cache: {element.path} : {element.name}")

    def __str__(self):
        return self._cache.__str__()


def main():
    import traffic
    import secret

    settings = secret.read_env_file("settings.env")
    ENV = secret.read_env_file("global.env")
    ghtraffic = traffic.Traffic(ENV["GHKEY"], settings)

    c = RftCache("test_cache.bson", ghtraffic)
    c.integrate()
    print(c)

if __name__ == "__main__":
    main()