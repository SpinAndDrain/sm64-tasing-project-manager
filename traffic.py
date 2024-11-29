import github
import json
import re
import cache


def pack_id(project, stage, star, time):

    result = ""
    keep_going = True

    def _combine(obj, prefix):
        nonlocal result
        nonlocal keep_going
        if not keep_going:
            return
        if not obj:
            keep_going = False
            return
        result += f"{prefix}{obj}"

    _combine(project, "")
    _combine(stage, "_")
    _combine(star, "-")
    _combine(time, ".")

    return result


def unpack_id(id_string):

    keep_going = True

    def _extract(sep):
        nonlocal keep_going
        nonlocal id_string
        if not keep_going:
            return None
        idx = id_string.find(sep)
        if idx == -1:
            keep_going = False
            return id_string
        tmp = id_string[:idx]
        id_string = id_string[idx+1:]
        return tmp
    
    return _extract('_'), _extract('-'), _extract('.'), _extract('\0')


def _safe_get(dic, key, default):
    return dic[key] if isinstance(dic, dict) and key in dic else default


def _extract_number_from_end(s):
    match = re.search(r'\d+$', s)
    if match:
        return int(match.group())
    else:
        return None


def matches_stage(stage_pattern, stage_explicit):
    idx = stage_pattern.find("%")
    if idx == -1:
        return stage_pattern == stage_explicit
    np = int(stage_pattern[idx+1:])
    ne = _extract_number_from_end(stage_explicit) or 0
    return ne >= 1 and ne <= np


def get_invalid_upload_location_reason(uloc):
    if uloc == -1:
        return "invalid project"
    if uloc == -2:
        return "invalid stage"
    if uloc == -3:
        return "invalid star"
    if uloc == -4:
        return "time must be entirely numerical"
    if isinstance(uloc, str):
        return "invalid url"
    return "?"


class Traffic():
    def __init__(self, token, settings):
        self._github = github.Github(auth=github.Auth.Token(token))
        self._settings = settings
        self._trafficrepo = self._github.get_repo(self._settings["TRAFFIC_REPOSITORY"])
    
    def has_element(self, path_to_element):
        return self.get_element(path_to_element) != None

    def get_element(self, path_to_element):
        try:
            return self._trafficrepo.get_contents(path_to_element)
        except Exception as e:
            print(f"[Error] While retrieving element {path_to_element}: {e}")
            return None

    def upload(self, path, author, content, rtf_cache = None):
        try:
            result = self._trafficrepo.create_file(path, f"Upload by {author}", content, branch="main")
            if rtf_cache:
                rtf_cache.write(path, result['commit'].sha, False, author[author.rfind("/")+1:])
            return result['content'].download_url
        except Exception as e:
            print(f"[Error] While uploading {path} initiated by {author}: ", e)
            return None

    def get_urls(self, path):
        try:
            target = self._trafficrepo.get_contents(path)
            m64 = None
            st = None
            for content in target:
                if not m64 and content.name.endswith(".m64"):
                    m64 = content
                if not st and (content.name.endswith(".st") or content.name.endswith(".savestate")):
                    st = content
            return m64 and m64.download_url, st and st.download_url
        except Exception as e:
            print(f"[Error] While trying to retrieve download url of {path}: ", e)
            return None, None

    def get_author(self, path):
        try:
            commits = self._trafficrepo.get_commits(path=path)
            for commit in commits:
                m = commit.commit.message
                if m.startswith("Upload by"):
                    return m[m.rfind("/")+1:]
            return None
        except Exception as e:
            print(f"[Error] While trying to retrieve author information of {path}: ", e)
            return None

    def get_latest_commit_hash(self):
        try:
            commits = self._trafficrepo.get_commits()
            if commits and commits[0]:
                return commits[0].sha
            print("[Warning] Remote repository has no commits")
            return None
        except Exception as e:
            print(f"[Error] While trying to retrieve author information of {path}: ", e)
            return None

    def delete(self, path, author, rtf_cache = None):
        deletions = 0
        try:
            contents = self._trafficrepo.get_contents(path)
            for content in contents:
                if content.type == 'file':
                    result = self._trafficrepo.delete_file(content.path, f"Deleted by {author}", content.sha)
                    if rtf_cache:
                        rtf_cache.write(content.path, result['commit'].sha, True, None)
                    deletions += 1
            return True, deletions
        except Exception as e:
            print(f"[Error] While trying to delete file {path}: ", e)
            return False, deletions


class ProjectManager():
    def __init__(self, file_path="projects.json"):
        self._file_path = file_path
        try:
            with open(self._file_path, 'r') as f:
                self._data = json.load(f)
        except FileNotFoundError:
            print("[Warning] No projects.json file found")
            self._data = {}

    def publish_changes(self):
        try:
            with open(self._file_path, 'w') as f:
                json.dump(self._data, f)
            return True
        except IOError as e:
            print("[Error] Could not publish projects.json changes: ", e)
            return False

    def tree(self, project):
        tree = []
        stages = None

        project = project and project.lower()

        for k, v in self._data.items():
            abbreviation = v.get("abbreviation")
            if not project:
                tree.append(f"{k} ({abbreviation})")
            elif k == project or abbreviation == project:
                stages = _safe_get(v, "stages", {})
                break
        
        if not project:
            return tree
        
        if not stages:
            return f"Project {project} not found"

        maxkeylen = 0
        for k, v in stages.items():
            lk = len(k)
            if lk > maxkeylen:
                maxkeylen = lk
            extra = ""
            if isinstance(v, int):
                extra = (", ".join(str(i) for i in range(1, v + 1)))
            else:
                extra = ", ".join(v)
            #tree.append(f"{k}: {(", ".join(str(i) for i in range(1, v + 1))) if isinstance(v, int) else ", ".join(v)}")
            tree.append(f"{k}: {extra}")
        
        tree.append(maxkeylen)

        return tree

    def get_full_project_name(self, project):
        if not project:
            return None
        project = project and project.lower()
        for k, v in self._data.items():
            abbreviation = v.get("abbreviation")
            if k == project or abbreviation == project:
                return f"{k} ({abbreviation})"
        return None

    def get_project(self, project):
        project = project and project.lower()
        for k, v in self._data.items():
            if k == project or project == v.get("abbreviation"):
                return k, v
        return None, None

    def get_stage(self, project, stage):
        _, project = self.get_project(project)
        if not project:
            return None, None
        for k, v in project["stages"].items():
            if k == stage:
                return k, v
        return None, None

    def has_star(self, project, stage, star):
        _, stage = self.get_stage(project, stage)
        if not stage:
            return None
        return star in ([f"{i}" for i in range(1, stage + 1)] if isinstance(stage, int) else stage)
    
    def construct_upload_location(self, project_or_id, stage, star, time, key):
        if not stage:
            project_or_id, stage, star, time = unpack_id(project_or_id)
        pk, pv = self.get_project(project_or_id)
        if not pk:
            return -1
        if stage == '*':
            return f"{pv['abbreviation']}/misc/{star.strip().replace(' ', '_')}"
        sk, sv = self.get_stage(project_or_id, stage)
        if not sk:
            return -2
        if star == '*':
            return f"{pv['abbreviation']}/{sk}/misc/{time.strip().replace(' ', '_')}"
        if not self.has_star(project_or_id, stage, star):
            return -3
        if time == '*':
            return f"{pv['abbreviation']}/{sk}/{star}/misc/{key.strip().replace(' ', '_')}"
        if not time or not all(char.isdigit() for char in time):
            return -4
        return f"{pv['abbreviation']}/{stage}/{star}/{time}"
