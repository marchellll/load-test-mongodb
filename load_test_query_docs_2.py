from locust import between

from mongo_user import MongoUser, mongodb_task
from settings import DEFAULTS

import pymongo
from bson import json_util, ObjectId
import random
import json
import pandas as pd

class MongoSampleUser(MongoUser):
    """
    Generic sample mongodb workload generator
    """
    # no delays between operations
    wait_time = between(0.5, 1)

    def __init__(self, environment):
        super().__init__(environment)

    def on_start(self):
        """
        Executed every time a new test is started - place init code here
        """
        changes_indices = [
          pymongo.IndexModel([('entity_type', pymongo.ASCENDING)]),
          pymongo.IndexModel([('action_id', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)]),
          pymongo.IndexModel([('created_at', pymongo.DESCENDING)]),
          pymongo.IndexModel([('code', pymongo.ASCENDING)]),
        ]

        # prepare the collection
        self.actions_collection, _ = self.ensure_collection("2_actions", [])
        self.changes_collection, _ = self.ensure_collection("2_changes", changes_indices)

        entity_types_df = pd.read_csv('entity_types.csv')

        self.entity_types = []
        for _, row in entity_types_df.iterrows():
          self.entity_types.append(row['entity_type'])

    @mongodb_task(weight=int(DEFAULTS['AGG_PIPE_WEIGHT']))
    def run_aggregation_pipeline(self):
        """
        Run an aggregation pipeline on a secondary node
        """
        entity_type = self.faker.random_elements(elements=self.entity_types, length = 1)[0]
        print(entity_type)
        pipeline = [
            {
                '$match' : {
                    'entity_type' : entity_type,
                }
            },
            {
                '$sort': {
                    'created_at': -1
                }
            },

            {
                '$limit': 10
            },
            {
                '$lookup': {
                    'from': '2_changes',
                    'localField': 'uid',
                    'foreignField': 'action_id',
                    'as': 'changes'
                          pipeline: [
                            {
                              '$limit': 10,
                            },
                          ],
                }
            },
        ]

        result = list(self.actions_collection.aggregate(pipeline))

        # print("hehe")
        # print(json_util.dumps(result))

        # twitterDataFile = open("queried_docs_2.json", "w")
        # # magic happens here to make it pretty-printed
        # twitterDataFile.write(json_util.dumps(result, indent=2))
        # twitterDataFile.close()

        # make sure we fetch everything by explicitly casting to list
        return result