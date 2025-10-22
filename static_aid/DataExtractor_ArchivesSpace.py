import logging
from pathlib import Path

from asnake.aspace import ASpace
from static_aid import config
from static_aid.DataExtractor import DataExtractor

class DataExtractor_ArchivesSpace(DataExtractor):

    def __init__(self, update=False):
        super().__init__(update)
        self.aspace = ASpace(
            username=config.archivesSpace['user'],
            password=config.archivesSpace['password'],
            baseurl=config.archivesSpace['baseurl'],
        )
        self.repo = self.aspace.repositories(config.archivesSpace['repository'])

    def _run(self):
        last_export = self.get_last_export_time()
        self.make_destinations()
        
        updated_objects = self.get_updated_object_data(last_export)
        category_dirs = [d for d in Path(config.assets['src']).iterdir() if d.is_dir()]

        for dir in category_dirs:
            refids, new_refids = self.get_refids_from_files(dir)
        
            # Save updated data
            for obj in [u for u in updated_objects if u['ref_id'] in refids]:
                archival_object_id = obj['uri'].split("/")[-1]
                self.save_data_file(archival_object_id, obj, config.destinations[dir.name])

            # Save new data
            for r in new_refids:
                data = self.get_object_by_id(r)
                archival_object_id = data['uri'].split("/")[-1]
                self.save_data_file(archival_object_id, data, config.destinations[dir.name])
                
                resource_id = data['resource']['ref'].split("/")[-1]
                if not Path(config.destinations['collections'], f"{resource_id}.json").is_file():
                    resource = self.aspace.client.get(data['resource']['ref']).json()
                    self.save_data_file(resource_id, resource, config.destinations['collections'])

                if data.get('parent'):
                    parent_id = data['parent']['ref'].split("/")[-1]
                    if not Path(config.destinations['objects'], f"{parent_id}.json").is_file():
                        parent = self.aspace.client.get(data['parent']['ref']).json()
                        self.save_data_file(parent_id, parent, config.destinations['objects'])
                
                for container in data['instances']:
                    if container.get('sub_container'):
                        container_uri = container['sub_container']['top_container']['ref']
                        container_id = container_uri.split("/")[-1]
                        container = self.aspace.client.get(container_uri).json()
                        self.save_data_file(container_id, container, config.destinations['containers'])


    def find_tree(self, identifier):
        """Fetches a tree for a resource."""
        # TODO: this will need to be re-thought, since the tree endpoint is deprecated
        tree = self.aspace.client.get(
            "/repositories/{}/resources/{}/tree".format(config.archivesSpace['repository'], identifier)).json()
        self.save_data_file(identifier, tree, config.destinations['trees'])

    def log_fetch_start(self, fetch_type, last_export):
        if last_export > 0:
            logging.info('*** Getting a list of {} modified since %d ***'.format(fetch_type), last_export)
        else:
            logging.info('*** Getting a list of all {} ***'.format(fetch_type))

    def get_updated_resources(self, last_export):
        """Fetches and saves updated resource records and associated trees."""
        self.log_fetch_start("resources", last_export)
        for resource in self.repo.resources(with_params={'all_ids': True, 'modified_since': last_export}):
            resource_id = resource.uri.split("/")[-1]
            if resource.publish:
                self.save_data_file(resource_id, resource.json(), config.destinations['collections'])
                self.find_tree(resource_id)
            else:
                self.remove_data_file(resource_id, config.destinations['collections'])
                self.remove_data_file(resource_id, config.destinations['trees'])

    def get_updated_objects(self, last_export):
        """Fetches and saves updated archival objects and associated breadcrumbs."""
        self.log_fetch_start("objects", last_export)
        for archival_object in self.repo.archival_objects(with_params={'all_ids': True, 'modified_since': last_export}):
            archival_object_id = archival_object.uri.split("/")[-1]
            if archival_object.publish:
                self.save_data_file(archival_object_id, archival_object.json(), config.destinations['objects'])
                breadcrumbs = self.aspace.client.get(
                    "/repositories/{}/resources/{}/tree/node_from_root?node_ids[]={}&published_only=true".format(
                        config.archivesSpace['repository'],
                        archival_object.resource.ref.split("/")[-1],
                        archival_object_id))
                if breadcrumbs.status_code == 200:
                    self.save_data_file(archival_object_id, breadcrumbs.json(), config.destinations['breadcrumbs'])
            else:
                self.remove_data_file(archival_object_id, config.destinations['objects'])
                self.remove_data_file(archival_object_id, config.destinations['breadcrumbs'])

    def get_updated_agents(self, last_export):
        """Fetch and save updated agent data."""
        self.log_fetch_start("agents", last_export)
        for agent_type, destination_sfx in [
                ('corporate_entities', 'organizations'),
                ('families', 'families'),
                ('people',  'people'),
                ('software', 'software')]:
            for agent in getattr(self.aspace.agents, agent_type)(with_params={'all_ids': True, 'modified_since': last_export}):
                agent_id = agent.uri.split("/")[-1]
                if agent.publish:
                    self.save_data_file(agent_id, agent.json(), config.destinations[destination_sfx])
                else:
                    self.remove_data_file(agent_id, config.destinations[destination_sfx])

    def get_updated_subjects(self, last_export):
        """Fetch and save updated subject data."""
        self.log_fetch_start("subjects", last_export)
        for subject in self.aspace.subjects(with_params={'all_ids': True, 'modified_since': last_export}):
            subject_id = subject.uri.split("/")[-1]
            if subject.publish:
                self.save_data_file(subject_id, subject.json(), config.destinations['subjects'])
            else:
                self.remove_data_file(subject_id, config.destinations['subjects'])

    def get_refids_from_files(self, dir):
        refids = []
        new_refids = []
        if dir.is_dir():
            for fp in dir.iterdir():
                print(fp)
                if fp.is_dir() and len(fp.name) == 32:
                    refids.append(fp.stem)
                    if not Path(config.DATA_DIR, dir.name, f'{fp.stem}.json').exists():
                        new_refids.append(fp.stem)
        return refids, new_refids
    
    def get_updated_object_data(self, last_export):
        """Fetches updated archival object data."""
        self.log_fetch_start("objects", last_export)
        updated_data = []
        for archival_object in self.repo.archival_objects.with_params(all_ids=True, modified_since=last_export):
            updated_data.append(archival_object.json())
        return updated_data
    
    def get_object_by_id(self, refid):
        resp = self.aspace.client.get(f"/repositories/{config.archivesSpace['repository']}/find_by_id/archival_objects?ref_id[]={refid}").json()
        if len(resp['archival_objects']) != 1:
            raise Exception(f'Got more than one result for refid {refid}')
        return self.aspace.client.get(resp['archival_objects'][0]['ref']).json()