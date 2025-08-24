import random

class UtilsService:
    def get_random_member(self, member_list):
        return random.choice(member_list.split('|'))