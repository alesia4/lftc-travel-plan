class HashTable:

    def __init__(self, capacity=101):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _hash(self, key):
        text = str(key)
        hash_value = 0

        for character in text:
            hash_value = (
                hash_value * 31 + ord(character)
            ) % self.capacity

        return hash_value

    def insert(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]

        for i, (existing_key, existing_value) in enumerate(bucket):
            if existing_key == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self.size += 1

    def get(self, key, default=None):
        index = self._hash(key)
        bucket = self.buckets[index]

        for existing_key, value in bucket:
            if existing_key == key:
                return value

        return default

    def contains(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]

        for existing_key, value in bucket:
            if existing_key == key:
                return True

        return False

    def __len__(self):
        return self.size

    def display(self):
        for index, bucket in enumerate(self.buckets):
            if bucket:
                print(f"Bucket {index}: {bucket}")