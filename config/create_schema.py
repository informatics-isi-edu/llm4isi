#!/usr/bin/python


from deriva.core import DerivaServer, get_credential
from deriva.core.ermrest_model import builtin_types, Schema, Table, Column, Key, ForeignKey
from deriva.chisel import Model, Schema, Table, Column, Key, ForeignKey
import argparse


# add schema if not exist or update if exist
def create_schema_if_not_exist(model, schema_name, schema_comment=None):
    if schema_name not in model.schemas:
        schema = model.create_schema(Schema.define(schema_name, schema_comment))
        return schema
    else:
        schema = model.schemas[schema_name]
        return schema


# add table if exist or return table if it exists spec to it is given
def create_table_if_not_exist(schema, create_spec, delete_if_exist=False):
    table_name = create_spec["table_name"]
    if table_name not in schema.tables:
        table = schema.create_table(create_spec)
        return table
    else:
        table = schema.tables[table_name]
        if delete_if_exist:
            table.drop(cascade=True)
            table = schema.create_table(create_spec)
        return table


#    creates and adds vocabulary table(vocab_table) to the root table
def add_vocab_table(model, schema_name, root_table, vocab_table, annotations):
    schema = create_schema_if_not_exist(model, schema_name)
    if root_table not in schema.tables:
        raise KeyError('root_table: ' + root_table + ' not present in schema')
    root_table_value = model.schemas[schema_name].tables[root_table]
    table_def_vocab = Table.define_vocabulary(
        tname=vocab_table, curie_template='%s:{RID}' % schema_name, annotations=annotations
    )
    vocab_table = schema.create_table(table_def_vocab)
    root_table_value.add_reference(vocab_table)


def add_ermrest_client_fk_to_tables(schema, table_names):
    for table_name in table_names:
        table = schema.tables[table_name]
        try:
            table.create_fkey(ForeignKey.define(
                        ['RCB'],
                        'public', 'ERMrest_Client',
                        ['ID']
                    ))
        except Exception as e:
            print(e)
        try:
            table.create_fkey(ForeignKey.define(
                        ['RMB'],
                        'public', 'ERMrest_Client',
                        ['ID']
                    ))
        except Exception as e:
            print(e)


def define_table_Person():
    table_def = Table.define(
        'Person',
        column_defs=[
            Column.define('Name', builtin_types.text, nullok=False),
            Column.define('Identity', builtin_types.text),
            Column.define('ORCID', builtin_types.text),
        ],
        key_defs=[Key.define(["Name"])],
        fkey_defs=[
            ForeignKey.define(
                ['Identity'],
                'public', 'ERMrest_Client',
                ['ID']
            )
        ],
        acls=[]
    )
    return table_def


def define_table_Contract_Type():
    table_def = Table.define(
        'Contract_Type',
        column_defs=[
            Column.define('Name', builtin_types.text, nullok=False),
        ],
        key_defs=[Key.define(["Name"])]
    )
    return table_def


def define_table_Proposal_Customer():
    table_def = Table.define(
        'Proposal_Customer',
        column_defs=[
            Column.define('Name', builtin_types.text, nullok=False),
        ],
        key_defs=[Key.define(["Name"])]
    )
    return table_def


def define_table_Proposal_Sponsor():
    table_def = Table.define(
        'Proposal_Sponsor',
        column_defs=[
            Column.define('Name', builtin_types.text, nullok=False),
        ],
        key_defs=[Key.define(["Name"])]
    )
    return table_def


def define_table_Proposal_Status():
    table_def = Table.define(
        'Proposal_Status',
        column_defs=[
            Column.define('Name', builtin_types.text, nullok=False),
        ],
        key_defs=[Key.define(["Name"])]
    )
    return table_def


def define_table_Proposal():
    table_def = Table.define(
        'Proposal',
        column_defs=[
            Column.define('Proposal_Status', builtin_types.text),
            Column.define('Proposal_Number', builtin_types.int8),
            Column.define('Proposal_Name', builtin_types.text),
            Column.define('Submittal_Date', builtin_types.date),
            Column.define('Proposal_Start_Date', builtin_types.date),
            Column.define('Proposal_End_Date', builtin_types.date),
            Column.define('Duration_Months', builtin_types.int4),
            Column.define('Project_Investigator', builtin_types.text),
            Column.define('Proposal_Manager', builtin_types.text),
            Column.define('Proposal_Sponsor', builtin_types.text),
            Column.define('Proposal_Customer', builtin_types.text),
            Column.define('Contract_Type', builtin_types.text),
            Column.define('Proposal_Title', builtin_types.text),
            Column.define('Created_By', builtin_types.text)
        ],
        fkey_defs=[
            ForeignKey.define(
                ['Project_Investigator'],
                'llm4isi', 'Person',
                ['Name']
            ),
            ForeignKey.define(
                ['Proposal_Manager'],
                'llm4isi', 'Person',
                ['Name']
            ),
            ForeignKey.define(
                ['Contract_Type'],
                'llm4isi', 'Contract_Type',
                ['Name']
            ),
            ForeignKey.define(
                ['Proposal_Sponsor'],
                'llm4isi', 'Proposal_Sponsor',
                ['Name']
            ),
            ForeignKey.define(
                ['Proposal_Customer'],
                'llm4isi', 'Proposal_Customer',
                ['Name']
            ),
            ForeignKey.define(
                ['Proposal_Status'],
                'llm4isi', 'Proposal_Status',
                ['Name']
            )
        ]
    )
    return table_def


def define_asset_Proposal_Files(schema):
    table_def = Table.define_asset(
        sname=schema,
        tname='Proposal_Files',
        column_defs=[
            Column.define('Proposal_RID', builtin_types.ermrest_rid, nullok=False, comment='Associated Proposal')

        ],
        fkey_defs=[
            ForeignKey.define(
                ['Proposal_RID'],
                'llm4isi', 'Proposal',
                ['RID']
            )
        ]
    )
    return table_def


def define_table_Dataset():
    table_def = Table.define(
        tname='Dataset',
        column_defs=[
            Column.define('Description', builtin_types.text)
        ]
    )
    return table_def


def setup_tables(schema, delete_if_exist=False):
    table_names = ["Dataset", "Person", "Proposal_Status", "Proposal_Customer", "Proposal_Sponsor", "Contract_Type",
                   "Proposal"]
    for table in table_names:
        create_table_if_not_exist(schema, eval("define_table_%s()" % table), delete_if_exist)
    create_table_if_not_exist(schema, define_asset_Proposal_Files(schema), delete_if_exist)
    table_names.append("Proposal_Files")
    add_ermrest_client_fk_to_tables(schema, table_names)


def add_association_tables(schema, delete_if_exist=True):
    try:
        dataset_table = schema.tables["Dataset"]
        proposal_table = schema.tables["Proposal"]
        proposal_files_table = schema.tables["Proposal_Files"]
        if "Proposal_Dataset" in schema.tables:
            proposal_dataset = schema.tables["Proposal_Dataset"]
            if delete_if_exist:
                proposal_dataset.drop()
        if "Proposal_Files_Dataset" in schema.tables:
            proposal_files_dataset = schema.tables["Proposal_Files_Dataset"]
            if delete_if_exist:
                proposal_files_dataset.drop()
        proposal_dataset = schema.create_association(proposal_table, dataset_table)
        proposal_files_dataset = schema.create_association(proposal_files_table, dataset_table)
    except Exception as e:
        print(e)


def add_vocab_tables(model, schema_name):
    add_vocab_table(model,
                    schema_name,
                    root_table="Proposal_Files",
                    vocab_table="Proposal_File_Type",
                    annotations={"tag:misd.isi.edu,2015:display": {"name": "Proposal File Type"}})


def main(host, catalog_id, schema_name, delete_if_existing):
    model = Model.from_catalog(DerivaServer('https', host, get_credential(host)).connect_ermrest(catalog_id))
    schema = create_schema_if_not_exist(model, schema_name)
    setup_tables(schema, delete_if_existing)
    add_association_tables(schema, delete_if_existing)
    add_vocab_tables(model, schema_name)


# -- =================================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--schema', type=str, required=True)
    parser.add_argument('--catalog', type=str, required=True)
    parser.add_argument('--delete-if-existing', action="store_true")
    args = parser.parse_args()
    main(args.host, args.catalog, args.schema, args.delete_if_existing)
