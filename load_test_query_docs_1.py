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
        # prepare the collection
        indexes = [
          pymongo.IndexModel([('uid', pymongo.DESCENDING)], unique=True),
          pymongo.IndexModel([('changes.entity_type', pymongo.ASCENDING)]),
          pymongo.IndexModel([('actor_user_id', pymongo.ASCENDING)]),
          pymongo.IndexModel([('created_at', pymongo.DESCENDING)]),
          pymongo.IndexModel([('changes.code', pymongo.ASCENDING)]),
        ]
        self.actions_collection, _ = self.ensure_collection("1_actions", indexes)

        entity_types_df = pd.read_csv('entity_types.csv')

        self.entity_types = []
        for _, row in entity_types_df.iterrows():
          self.entity_types.append(row['entity_type'])


    @mongodb_task(weight=int(DEFAULTS['AGG_PIPE_WEIGHT']))
    def run_aggregation_pipeline(self):
        """
        Run an aggregation pipeline on
        """
        entity_type = self.faker.random_elements(elements=self.entity_types, length = 1)[0]
        print(entity_type)
        pipeline = [
            {
                '$match' : {
                    'changes.entity_type' : entity_type,
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
        ]

        result = list(self.actions_collection.aggregate(pipeline=pipeline, allowDiskUse=True))

        # print("hehe")
        # print(json_util.dumps(result))

        twitterDataFile = open("queried_docs_1.json", "w")
        # magic happens here to make it pretty-printed
        twitterDataFile.write(json_util.dumps(result, indent=2))
        twitterDataFile.close()

        # make sure we fetch everything by explicitly casting to list
        return result