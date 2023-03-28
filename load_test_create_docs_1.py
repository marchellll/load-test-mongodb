from locust import between

from mongo_user import MongoUser, mongodb_task
from settings import DEFAULTS

import pymongo
import random

from datetime import datetime


import pandas as pd


class MongoSampleUser(MongoUser):
    """
    Generic sample mongodb workload generator
    """
    # no delays between operations
    wait_time = between(0.01, 0.1)

    def __init__(self, environment):
        super().__init__(environment)

    def on_start(self):
        """
        Executed every time a new test is started - place init code here
        """

        indexes = [
          pymongo.IndexModel([('uid', pymongo.DESCENDING)], unique=True),
          pymongo.IndexModel([('changes.entity_type', pymongo.ASCENDING)]),
          pymongo.IndexModel([('actor_user_id', pymongo.ASCENDING)]),
          pymongo.IndexModel([('created_at', pymongo.DESCENDING)]),
          pymongo.IndexModel([('changes.code', pymongo.ASCENDING)]),
        ]

        # prepare the collection
        self.actions_collection, _ = self.ensure_collection("1_actions", indexes)

        actions_df = pd.read_csv('actions.csv')
        entity_types_df = pd.read_csv('entity_types.csv')

        self.actions = []
        self.entity_types = []

        for _, action in actions_df.iterrows():
          print(action['uuid'])
          document = {
            'uid': action['uuid'],
            'actor_user_id': action['actor_id'],
            'created_at': datetime.today(),
          }

          result = self.actions_collection.update_one({ 'uid': action['uuid'] }, { '$set': document }, upsert=True )
          self.actions.append(document)

        for _, row in entity_types_df.iterrows():
          self.entity_types.append(row['entity_type'])

        # for uuid in self.action_ids:
        #   document = {
        #     'uid': uuid,
        #     'actor_user_id': self.faker.pyint(min_value=0, max_value=100000),
        #     'created_at': datetime.today().replace(microsecond=0),
        #   }

        # for _ in range(2):
        #   uid = self.faker.uuid4()
        #   document = {
        #     'uid': uid,
        #     'actor_user_id': self.faker.pyint(min_value=0, max_value=100000),
        #     'created_at': datetime.today().replace(microsecond=0),
        #   }
        #   result = self.actions_collection.insert_one(document)
        #   self.action_ids.append(uid)


    def before_after(self, entity_id):
      data = {
        'id': entity_id,
        'slabs': [],
      }

      # simulate 200 fields with arguably big string (300 in length)
      for it in range(200):
        data[self.faker.word()] = self.faker.text(max_nb_chars=300)


      # a bit more extra data
      for _ in range(self.faker.pyint(min_value=1, max_value=10)):
        data['slabs'] += [{
            'id': self.faker.uuid4(),
            'min': self.faker.pyint(min_value=0, max_value=100),
            'max': self.faker.pyint(min_value=0, max_value=100),
            'membership_fee_type': self.faker.random_elements(elements=('fixed', 'value', 'hybrid'), length=1)[0],
            'membership_fee': self.faker.pyint(min_value=0, max_value=100),
            'membership_fee_rate': self.faker.pyint(min_value=0, max_value=100),
            'membership_fee_discount_type': self.faker.random_elements(elements=('fixed', 'value', 'hybrid'), length=1)[0],
            'membership_fee_discount': self.faker.pyint(min_value=0, max_value=100),
            'membership_fee_discount_rate': self.faker.pyint(min_value=0, max_value=100),
            'contribution_type': self.faker.random_elements(elements=('fixed', 'value', 'hybrid'), length=1)[0],
            'contribution_amount': self.faker.pyint(min_value=0, max_value=100),
          }]

      return data


    def generate_new_document(self):
        """
        Generate a new sample document
        """
        action = self.faker.random_elements(elements=self.actions, length = 1)[0]
        entity_id = self.faker.uuid4()

        document = {
          'action_id': action['uid'],
          'entity_type': self.faker.random_elements(elements=self.entity_types, length = 1)[0],
          'entity_id': entity_id,
          'code': self.faker.word(),
          'before': self.before_after(entity_id),
          'after': self.before_after(entity_id),
        }
        return document

    @mongodb_task(weight=1000)
    def insert_single_document(self):
        document = self.generate_new_document()

        self.actions_collection.update_one({'uid': document['action_id']}, { '$push': { 'changes': document } })