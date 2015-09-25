from rdflib.namespace import Namespace
from ckanext.dcat.profiles import RDFProfile

DCT = Namespace("http://purl.org/dc/terms/")


class VLDCATAPProfile(RDFProfile):
    '''
    An RDF profile for the Swedish DCAT-AP recommendation for data portals

    It requires the European DCAT-AP profile (`euro_dcat_ap`)
    '''

    def parse_dataset(self, dataset_dict, dataset_ref):

        # Extra resource for dc:source (TDT)
        if (dataset_ref, DCT.source, None) in self.g:
            resource_dict = {
                'url': self.g.value(dataset_ref, DCT.source),
                'uri': None}
            dataset_dict['resources'].append(resource_dict)

        # Spatial label
        if not dataset_dict['resources'][0]['url']:
            dataset_dict['resources'][0]['url'] = dataset_dict['resources'][0]['uri']

        # Licenses : if no license, take license from first resoure
        if not 'license_id' in dataset_dict and 'resources' in dataset_dict:
            for res in dataset_dict['resources']:
                if 'license' in res:
                    dataset_dict['license_id'] = res['license']
                    break

        return dataset_dict