class HashTable:
    def __init__(self, capacity=101):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _hash(self, key):
        text = str(key)
        hash_value = 0

        for character in text:
            hash_value = (hash_value * 31 + ord(character)) % self.capacity

        return hash_value

    def insert(self, key):
        bucket_index = self._hash(key)
        bucket = self.buckets[bucket_index]

        for position, existing_key in enumerate(bucket):
            if existing_key == key:
                return bucket_index, position

        position = len(bucket)
        bucket.append(key)
        self.size += 1

        return bucket_index, position

    def get(self, key):
        bucket_index = self._hash(key)
        bucket = self.buckets[bucket_index]

        for position, existing_key in enumerate(bucket):
            if existing_key == key:
                return bucket_index, position

        return None

    def __len__(self):
        return self.size

    def get_entries(self):
        entries = []

        for bucket_index, bucket in enumerate(self.buckets):
            for position, key in enumerate(bucket):
                entries.append((bucket_index, position, key))

        return entries