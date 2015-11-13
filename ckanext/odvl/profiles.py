from rdflib.namespace import Namespace
from ckanext.dcat.profiles import RDFProfile
import ckan.model as model

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

        licenses = model.Package.get_license_register().licenses

        # Licenses : if no license, take license from first resoure
        if not 'license_id' in dataset_dict and 'resources' in dataset_dict:
            for res in dataset_dict['resources']:
                if 'license' in res:
                    matching_license_id = next((lic for lic in licenses if (lic['id'] == res['license'] or lic['url'] == res['license']) ), None)
                    if matching_license_id:
                        dataset_dict['license_id'] = matching_license_id
                    else:
                        dataset_dict['license_id'] = res['license']
                    break

        return dataset_dict