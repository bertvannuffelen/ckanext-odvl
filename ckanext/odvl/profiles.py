from rdflib.namespace import Namespace
from ckanext.dcat.profiles import RDFProfile
import ckan.model as model
from rdflib import URIRef, BNode, Literal

from rdflib.namespace import Namespace, RDF, XSD, SKOS, RDFS
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
VODAP = Namespace("http://data.vlaanderen.be/ns/vodap#")

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
        if len(dataset_dict['resources']) > 0 and not dataset_dict['resources'][0]['url']:
            dataset_dict['resources'][0]['url'] = dataset_dict['resources'][0]['uri']

        licenses = model.Package.get_license_register().licenses

        # Licenses
        dataset_license = self._object_value(dataset_ref, DCT.license)
        if 'license_id' in dataset_dict:
            # there's a license_id already, use it
            dataset_dict['license_id'] = dataset_dict['id']
        else:
            license_value = None
            if dataset_license:
                license_value = dataset_license
            elif 'resources' in dataset_dict:
                #if no license, take license from first resource
                for res in dataset_dict['resources']:
                    if 'license' in res:
                        license_value = res['license']
                        break

            if license_value:
                # look for matching license in registered licenses
                matching_license = next(
                    (lic for lic in licenses if (lic['id'] == license_value or
                                                 lic['url'] == license_value or
                                                 lic['title'] == license_value)),
                    None)
                if matching_license:
                    dataset_dict['license_id'] = matching_license['id']
                else:
                    # unknown license value
                    dataset_dict['license_id'] = license_value

                    # TODO uncomment this to tag license as notrecognized
                    #dataset_dict['license_id'] = 'notrecognized'
                    #if '://' in license_value:
                    #    dataset_dict['license_url'] = license_value
                    #else:
                    #    dataset_dict['license_title'] = license_value
            else:
                # no license found anywhere
                dataset_dict['license_id'] = 'notspecified'

        extras = {}
        for extra in dataset_dict['extras']:
            extras[extra['key']] = extra

        # Take contact as maintainer
        if not 'maintainer_email' in dataset_dict:
            if 'contact_email' in extras:
                dataset_dict['maintainer_email'] = extras['contact_email']['value']
            if 'contact' in extras:
                dataset_dict['maintainer'] = extras['contact']['value']
            if 'contact_uri' in extras:
                dataset_dict['maintainer_uri'] = extras['contact_uri']['value']

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        g = self.g
        licenses = model.Package.get_license_register().licenses
        if hasattr(self, 'validation_mode') and self.validation_mode:
            g.bind('vodap', VODAP)

            org_id = self._get_dataset_value(dataset_dict, 'owner_org')
            g.add((dataset_ref, VODAP['ckan-organisation'], Literal(org_id)))
            org = model.Group.get(org_id)
            if (org):
                g.add((dataset_ref, VODAP['ckan-organisation-name'], Literal(org.name)))

        if ('license_id' in dataset_dict):
            matching_license = next(
                (lic for lic in licenses if (lic['id'] == dataset_dict.get('license_id'))),
                None)
            # check if resources have a license already
            if matching_license:
                for resource in g.subjects(RDF.type, DCAT.Distribution):
                    if (resource, DCT.license, None) not in g:
                        g.add((resource, DCT.license, URIRef(matching_license['url'])))
