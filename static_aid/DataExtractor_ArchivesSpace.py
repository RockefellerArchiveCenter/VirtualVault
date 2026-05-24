import json
from datetime import datetime
from os import getenv
from pathlib import Path

from asnake.aspace import ASpace

from static_aid import config
from static_aid.DataExtractor import DataExtractor


class DataExtractor_ArchivesSpace(DataExtractor):

    def __init__(self, update=False):
        super().__init__(update)
        self.aspace = ASpace(
            username=getenv('AS_USERNAME'),
            password=getenv('AS_PASSWORD'),
            baseurl=getenv('AS_BASEURL'),
        )
        self.repo = self.aspace.repositories(
            config.archivesSpace['repository'])

    def _run(self):
        last_export = self.get_last_export_time()
        self.make_destinations()

        category_dirs = [
            d for d in Path(
                config.assets['src']).iterdir() if d.is_dir()]

        for dir in category_dirs:
            refids, new_refids = self.get_refids_from_files(dir, last_export)
            print(f"Found {len(refids)} refids and {len(new_refids)} new refids in {dir.stem} directory.")

            for refid_chunk in self.list_chunks(refids):
                updated_data = self.get_updated_data(refid_chunk, last_export)
                for obj in updated_data:
                    archival_object_id = obj['uri'].split("/")[-1]
                    self.save_data_file(archival_object_id, obj,
                                        config.destinations[dir.name])

                    if obj['ref_id'] in new_refids:
                        resource_id = obj['resource']['ref'].split("/")[-1]
                        if not Path(config.destinations['collections'], f"{resource_id}.json").is_file():
                            resource = self.aspace.client.get(
                                obj['resource']['ref']).json()
                            self.save_data_file(
                                resource_id, resource, config.destinations['collections'])

                        if obj.get('parent'):
                            parent_id = obj['parent']['ref'].split("/")[-1]
                            if not Path(
                                    config.destinations['objects'], f"{parent_id}.json").is_file():
                                parent = self.aspace.client.get(
                                    obj['parent']['ref']).json()
                                self.save_data_file(
                                    parent_id, parent, config.destinations['objects'])

                        for container in obj['instances']:
                            if container.get('sub_container'):
                                container_uri = container['sub_container']['top_container']['ref']
                                container_id = container_uri.split("/")[-1]
                                container = self.aspace.client.get(
                                    container_uri).json()
                                self.save_data_file(
                                    container_id, container, config.destinations['containers'])

    def get_refids_from_files(self, dir, last_export):
        refids = []
        new_refids = []
        if dir.is_dir():
            for fp in dir.iterdir():
                if fp.is_dir() and len(fp.name) == 32:
                    refids.append(fp.stem)
                    created_time = fp.stat().st_ctime
                    if created_time >= last_export:
                        new_refids.append(fp.stem)
        return refids, new_refids

    def list_chunks(self, lst, n=30):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def get_updated_data(self, refid_list, last_export):
        """Returns results for a list of refids modified after a given date"""
        refid_value = " OR ".join(refid_list)
        if last_export:
            print(f"Fetching {len(refid_list)} refids modified since {last_export}")
            last_export_datetime = datetime.fromtimestamp(last_export)
            last_export_datestring = last_export_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            query = json.dumps({"query": {"jsonmodel_type": "range_query", "field": "system_mtime", "from": last_export_datestring}})
            url = f'/repositories/2/search?q=refid:{refid_value}&filter={query}&fields[]=json&page=1'
        else:
            print(f"Fetching all {len(refid_list)} refids")
            url = f'/repositories/2/search?q=refid:{refid_value}&fields[]=json&page=1'
        resp = self.aspace.client.get_paged(url)
        for r in resp:
            yield json.loads(r['json'])
