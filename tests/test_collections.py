import unittest

from akl.collections import LRUDict


class TestLRUDict(unittest.TestCase):
    def test_init_with_max_size(self):
        """Test initializing with a max_size."""
        lru = LRUDict(max_size=5)
        self.assertEqual(lru.max_size, 5)
        self.assertEqual(len(lru), 0)

    def test_init_with_items(self):
        """Test initializing with items."""
        lru = LRUDict({"a": 1, "b": 2}, max_size=5)
        self.assertEqual(lru, {"a": 1, "b": 2})
        self.assertEqual(len(lru), 2)

    def test_init_with_invalid_max_size(self):
        """Test initializing with an invalid max_size."""
        with self.assertRaises(AssertionError):
            LRUDict(max_size=0)
        with self.assertRaises(AssertionError):
            LRUDict(max_size=-1)

    def test_setitem(self):
        """Test setting an item moves it to the end of the order."""
        lru = LRUDict(max_size=3)
        lru["a"] = 1
        lru["b"] = 2
        lru["c"] = 3
        self.assertEqual(list(lru.keys()), ["a", "b", "c"])

        # Setting an existing item should move it to the end
        lru["a"] = 4
        self.assertEqual(list(lru.keys()), ["b", "c", "a"])
        self.assertEqual(lru["a"], 4)

    def test_getitem(self):
        """Test getting an item moves it to the end of the order."""
        lru = LRUDict(max_size=3)
        lru["a"] = 1
        lru["b"] = 2
        lru["c"] = 3
        self.assertEqual(list(lru.keys()), ["a", "b", "c"])

        # Getting an item should move it to the end
        _ = lru["a"]
        self.assertEqual(list(lru.keys()), ["b", "c", "a"])

    def test_max_size_enforcement(self):
        """Test that the LRU dict removes oldest items when max_size is reached."""
        lru = LRUDict(max_size=3)
        lru["a"] = 1
        lru["b"] = 2
        lru["c"] = 3
        self.assertEqual(len(lru), 3)
        self.assertEqual(set(lru.keys()), {"a", "b", "c"})

        # Adding a 4th item should remove the oldest (a)
        lru["d"] = 4
        self.assertEqual(len(lru), 3)
        self.assertEqual(set(lru.keys()), {"b", "c", "d"})

        # Accessing 'b' makes it newest, adding 'e' should remove 'c'
        _ = lru["b"]
        lru["e"] = 5
        self.assertEqual(len(lru), 3)
        self.assertEqual(set(lru.keys()), {"b", "d", "e"})

    def test_update_existing_preserves_order(self):
        """Test that updating an existing item preserves the LRU order."""
        lru = LRUDict(max_size=3)
        lru["a"] = 1
        lru["b"] = 2
        lru["c"] = 3

        # Update 'b' without moving it to end
        lru["b"] = 22
        self.assertEqual(list(lru.keys()), ["a", "c", "b"])

        # Add a new item that forces eviction
        lru["d"] = 4
        self.assertEqual(set(lru.keys()), {"c", "b", "d"})
        self.assertEqual(lru["b"], 22)  # Value was updated

    def test_key_error_for_missing_key(self):
        """Test that accessing a non-existent key raises KeyError."""
        lru = LRUDict(max_size=3)
        lru["a"] = 1

        with self.assertRaises(KeyError):
            _ = lru["b"]


if __name__ == "__main__":
    unittest.main()
