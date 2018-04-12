from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# Module API

class DataHub(object):
    """
    DataHub class is used to interact with the DataHub server.
    Authentication is done under the hood.
    API_Key could be found on the DataHub user page.

    From the program side DataHub class gives you methods to
        - init a new data-package from the existing data file(s)

    !   - validate data & schema in the data-package
    !     (validation may be implemented in the Package class, we
    !      are not sure yet)

        - push a data-package to the datahub
        - search data-packages on the datahub
        - open a data-package from the datahub
          (could open private data-packages too, if belongs to user)


    From the DataHub server side this class represents one particular
    authorized client.
    We use JWT (javascript web token) to authenticate the client.

    This class will work with invalid or absent secure token,
    but will raise Errors, when trying to
        - push package
        - get private package
    """

    def __init__(self, api_key='', api_address='https://api.datahub.io'):
        """
        While initiating the instance, the method also checks if
        the api_key (JWT token) is valid and tries to get user
        information from the server.
        :param api_key:
        :param api_address:
        """
        self.api_key = api_key
        self.api_address = api_address

        # get user info from server, using the api_key
        # ..
        pass

        self.user = {
            # should be in the server response:
            # id, name, username, email, provider_id, join_date
        }

    # TODO: rename 'init' to 'init_data_package' ?
    # This method initiates a data-package, not the class instance :)
    # May be we should rename it more obviously?
    def init(self, path, interactive=False):
        """
        Init a new data-package or update an existing one.
        Data-package specification:
            https://frictionlessdata.io/docs/data-package/

        :param path: String:
            - path to single file
            - path to folder where you suppose to init a data-package
        :param interactive:
        :return:
        """
        raise NotImplementedError
        return package

    def validate(self, package):
        raise NotImplementedError

    def push(self, package):
        """
        Uploads a package (dataset) to the DataHub server.

        :param package: data-package instance
        :return: !!! not defined yet
        """
        raise NotImplementedError

    def search(self, keywords):
        """
        Search packages on the DataHub server.
        :param keywords:
        :return:
        """
        raise NotImplementedError

    def open(self, source):
        """
        Opens a package from the DataHub server.

        :param source: String, one of
            - datasetId:        [owner/]package[/version_index]
            - dataset URL:      http://datahub.io/core/gdp/[v/10]
            - descriptor URL:   http://datahub.io/core/gdp/datapackage.json
        :return: data-package object
        """
        raise NotImplementedError
        return package


