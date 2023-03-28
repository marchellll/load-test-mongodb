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

        changes_indices = [
          pymongo.IndexModel([('entity_type', pymongo.ASCENDING)]),
          pymongo.IndexModel([('action_id', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)]),
          pymongo.IndexModel([('created_at', pymongo.DESCENDING)]),
          pymongo.IndexModel([('code', pymongo.ASCENDING)]),
        ]

        action_indices = [
          pymongo.IndexModel([('uid', pymongo.ASCENDING), ('created_at', pymongo.DESCENDING)]),
          pymongo.IndexModel([('actor_user_id', pymongo.ASCENDING), ('created_at', pymongo.DESCENDING)]),
          pymongo.IndexModel([('created_at', pymongo.DESCENDING)]),
        ]

        # prepare the collection
        self.actions_collection, _ = self.ensure_collection("2_actions", action_indices)
        self.changes_collection, _ = self.ensure_collection("2_changes", changes_indices)


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


    def before_after(self, entity_id):
      data = {
        'id': entity_id,
        'grade': self.faker.job(),
        'access_rate': self.faker.pyint(min_value=0, max_value=100),
        'max_count': self.faker.pyint(min_value=0, max_value=100),
        'static_increment': self.faker.pyint(min_value=0, max_value=100),
        'slabs': [],
        'created_at': datetime.today().replace(microsecond=0),
      }

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
        entity_id = self.faker.uuid4()
        action = self.faker.random_elements(elements=self.actions, length = 1)[0]
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
    def insert_one_group_and_many_docs(self):
        document = self.generate_new_document()
        with self.ayo_start_session() as session:
          with session.start_transaction():
            self.changes_collection.insert_one(document)
            self.actions_collection.update_one(
              { 'uid': document['action_id'] },
              { '$addToSet': { 'entity_type': document['entity_type'] } },
              session=session
            )