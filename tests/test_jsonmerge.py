# vim:ts=4 sw=4 expandtab softtabstop=4
import unittest
import jsonmerge

class TestMerge(unittest.TestCase):

    def test_default(self):

        schema = {}

        base = None
        base = jsonmerge.merge(base, "a", schema)
        base = jsonmerge.merge(base, "b", schema)

        self.assertEqual(base, "b")

    def test_overwrite(self):

        schema = {'mergeStrategy': 'overwrite'}

        base = None
        base = jsonmerge.merge(base, "a", schema)
        base = jsonmerge.merge(base, "b", schema)

        self.assertEqual(base, "b")

    def test_version(self):

        schema = {'mergeStrategy': 'version'}

        base = None
        base = jsonmerge.merge(base, "a", schema)
        base = jsonmerge.merge(base, "b", schema)

        self.assertEqual(base, [{'value': "a"}, {'value': "b"}])

    def test_version_meta(self):

        schema = {'mergeStrategy': 'version'}

        merger = jsonmerge.Merger(schema)

        base = None
        base = merger.merge(base, "a", meta={'uri': 'http://example.com/a'})
        base = merger.merge(base, "b", meta={'uri': 'http://example.com/b'})

        self.assertEqual(base, [
            {'value': "a",
            'uri': 'http://example.com/a' },
            {'value': "b",
            'uri': 'http://example.com/b' }])

    def test_version_last(self):

        schema = {  'mergeStrategy': 'version',
                    'mergeOptions': { 'limit': 1 } }

        base = None
        base = jsonmerge.merge(base, "a", schema)
        base = jsonmerge.merge(base, "b", schema)

        self.assertEqual(base, [{'value': "b"}])

    def test_append(self):

        schema = {'mergeStrategy': 'append'}

        base = None
        base = jsonmerge.merge(base, ["a"], schema)
        base = jsonmerge.merge(base, ["b"], schema)

        self.assertEqual(base, ["a", "b"])

    def test_append_type_error(self):

        schema = {'mergeStrategy': 'append'}

        base = None
        self.assertRaises(TypeError, jsonmerge.merge, base, "a", schema)

    def test_merge_default(self):

        schema = {}

        base = None
        base = jsonmerge.merge(base, {'a': "a"}, schema)
        base = jsonmerge.merge(base, {'b': "b"}, schema)

        self.assertEqual(base, {'a': "a",  'b': "b"})

    def test_merge_empty_schema(self):

        schema = {}

        base = None
        base = jsonmerge.merge(base, {'a': {'b': 'c'}}, schema)

        self.assertEqual(base, {'a': {'b': 'c'}})

    def test_merge_trivial(self):

        schema = {'mergeStrategy': 'objectMerge'}

        base = None
        base = jsonmerge.merge(base, {'a': "a"}, schema)
        base = jsonmerge.merge(base, {'b': "b"}, schema)

        self.assertEqual(base, {'a': "a",  'b': "b"})

    def test_merge_type_error(self):

        schema = {'mergeStrategy': 'objectMerge'}

        base = None
        self.assertRaises(TypeError, jsonmerge.merge, base, "a", schema)

    def test_merge_overwrite(self):

        schema = {'mergeStrategy': 'objectMerge'}

        base = None
        base = jsonmerge.merge(base, {'a': "a"}, schema)
        base = jsonmerge.merge(base, {'a': "b"}, schema)

        self.assertEqual(base, {'a': "b"})

    def test_merge_append(self):

        schema =    {
                        'mergeStrategy': 'objectMerge',
                        'properties': {
                            'a': {'mergeStrategy': 'append' }
                        }
                    }

        base = None
        base = jsonmerge.merge(base, {'a': ["a"]}, schema)
        base = jsonmerge.merge(base, {'a': ["b"], 'b': 'c'}, schema)

        self.assertEqual(base, {'a': ["a", "b"], 'b': 'c'})

    def test_merge_append_pattern(self):

        schema =    {
                        'mergeStrategy': 'objectMerge',
                        'patternProperties': {
                            'a': {'mergeStrategy': 'append' }
                        }
                    }

        base = None
        base = jsonmerge.merge(base, {'a': ["a"]}, schema)
        base = jsonmerge.merge(base, {'a': ["b"], 'b': 'c'}, schema)

        self.assertEqual(base, {'a': ["a", "b"], 'b': 'c'})

    def test_merge_append_additional(self):

        schema =    {
                        'mergeStrategy': 'objectMerge',
                        'additionalProperties': {
                            'a': {'mergeStrategy': 'append' }
                        }
                    }

        base = None
        base = jsonmerge.merge(base, {'a': ["a"]}, schema)
        base = jsonmerge.merge(base, {'a': ["b"], 'b': 'c'}, schema)

        self.assertEqual(base, {'a': ["a", "b"], 'b': 'c'})


    def test_example(self):

        head1 =     {
                        'buyer': {
                            'id': {
                                'name': "Test old",
                            },
                            'uri': 'Test uri old',
                        }
                    }

        head2 =     {
                        'buyer': {
                            'id': {
                                'name': "Test new"
                            },
                            'uri': 'Test uri new',
                        },

                        'award': "Award"
                    }

        base_expect = {
                        'buyer': {
                            'id': {
                                'name': [
                                    {'value': "Test old" },
                                    {'value': "Test new" },
                                ]
                            },
                            'uri': 'Test uri new',
                        },

                        'award': "Award"
                    }

        schema =    {
                        'mergeStrategy': 'objectMerge',
                        'properties': {
                            'buyer': {
                                'properties': {
                                    'id': {
                                        'properties': {
                                            'name': {
                                                'mergeStrategy': 'version',
                                            }
                                        }
                                    },
                                    'uri': {
                                        'mergeStrategy': 'overwrite',
                                    }
                                },
                            },
                            'award': {
                                'mergeStrategy': 'overwrite',
                            }
                        },
                    }

        base = None
        base = jsonmerge.merge(base, head1, schema)
        base = jsonmerge.merge(base, head2, schema)

        self.assertEqual(base, base_expect)

    def test_refs(self):

        schema =    {
                        'properties': {
                            'a': {'$ref': "#/definitions/a"},
                        },
                        'definitions': {
                            "a": {
                                "properties": {
                                    "b": { 'mergeStrategy': 'version' },
                                }
                            },
                        }
                    }

        merger = jsonmerge.Merger(schema)

        base = None
        base = merger.merge(base, {"a": {"b": "c"} })
        base = merger.merge(base, {"a": {"b": "d"} })

        self.assertEqual(base, {"a": {"b": [{"value": "c"}, {"value": "d"}] } })

    def test_oneof(self):

        schema =    {
                        'oneOf': [
                            { 'properties': { 'a': {} } },
                            { 'properties': { 'b': {} } }
                        ]
                    }

        merger = jsonmerge.Merger(schema)

        base = None
        base = merger.merge(base, {'a': 1})
        base = merger.merge(base, {'b': 2})

        self.assertEqual(base, {'a': 1, 'b': 2})

class TestGetSchema(unittest.TestCase):

    def test_default_overwrite(self):
        schema = { 'description': 'test' }

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema()

        self.assertEqual(schema2, { 'description': 'test' })

    def test_default_object_merge(self):
        schema = { 'properties': {
                        'foo': {
                            'mergeStrategy': 'version',
                        }
                } }

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema()

        self.assertEqual(schema2, { 'properties': {
                                        'foo': {
                                            'items': {
                                                'properties': {
                                                    'value': {},
                                                }
                                            }
                                        }
                                    }
                                 } )

    def test_overwrite(self):
        schema = {'mergeStrategy': 'overwrite'}

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema()

        self.assertEqual(schema2, {})

    def test_append(self):
        schema = {  'type': 'array',
                    'mergeStrategy': 'append' }

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema()

        self.assertEqual(schema2, {'type': 'array'})

    def test_version(self):
        schema = {  'mergeStrategy': 'version' }

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema()

        self.assertEqual(schema2,
                {
                    'items': {
                        'properties': {
                            'value': {}
                        }
                    }
                })

    def test_version_meta(self):
        schema = {  'type': 'object',
                    'mergeStrategy': 'version' }

        meta =  {   'properties': {
                        'date': {},
                        'version': {}
                    }
                }

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema(meta)

        self.assertEqual(schema2,
                {
                    'items': {
                        'properties': {
                            'value': { 'type': 'object' },
                            'date': {},
                            'version': {}
                        }
                    }
                })

    def test_version_limit(self):
        schema = {  'mergeStrategy': 'version',
                    'mergeOptions': { 'limit': 5 } }

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema()

        self.assertEqual(schema2,
                {
                    'items': {
                        'properties': {
                            'value': {}
                        }
                    },
                    'maxItems': 5
                })

    def test_object_merge_simple(self):
        schema = {  'mergeStrategy': 'objectMerge' }

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema()

        self.assertEqual(schema2, {})

    def test_object_merge_nested(self):
        schema =    {   'mergeStrategy': 'objectMerge',
                        'properties': {
                            'foo': {
                                'mergeStrategy': 'version',
                            }
                         }
                    }

        merger = jsonmerge.Merger(schema)
        schema2 = merger.get_schema()

        self.assertEqual(schema2,
                {   'properties': {
                        'foo': {
                            'items': {
                                'properties': {
                                    'value': {}
                                }
                            }
                        }
                    }
                })

    def test_oneof(self):

        schema =    {
                        'mergeStrategy': 'objectMerge',
                        'oneOf': [
                            { 'properties': { 'a': {} } },
                            { 'properties': { 'b': {} } }
                        ]
                    }

        merger = jsonmerge.Merger(schema)
        self.assertRaises(TypeError, merger.get_schema)
