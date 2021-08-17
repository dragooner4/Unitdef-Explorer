# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import yaml
import os
from pyvis import network as net
from pyvis.network import Network
import networkx as nx


def dependencies(variable, unitdef):
    print('Dependencies for', variable, 'in', unitdef['dlpc']['units'][0]['name'])

    print("\n ----- Variables -----")
    for var in unitdef['dlpc']['vars']:
        if var['type'] == 'VV' and variable in var['config']['function']:
            print(var['name'], '-', var['id'])

    print("\n ----- Actuators -----")
    for actuator in unitdef['dlpc']['actuators']:
        if variable in actuator['condition'] or variable in [action['expression'] for action in actuator['actions']]:
            print(actuator['name'], '-', actuator['id'])


def extract_variables(function_text: str, start_seq: str, stop_seq: str) -> list:
    variable_list = []
    end = -1
    start = -1
    for index, char in enumerate(function_text):
        # print(function_text[index:index + 2])
        if char == "{" or str_eql(function_text[index:index + len(start_seq)], start_seq):
            # print("Start", index)
            start = index
        if char == "}":
            end = index
        if str_eql(function_text[index:index + len(stop_seq)], stop_seq) and start != -1:
            end = index + len(stop_seq)
            # print("End", end)
        if end > start:
            variable = function_text[start + 1:end]
            variable_list.append(variable)
            start = -1
            end = -1
    return variable_list

def search_dcs_tags(tag_name, dcs_list):
    matches = [name for name in dcs_list if tag_name == name['id']]
    assert len(matches) <= 1, 'Found multiple dcs_tag_names'
    return matches is not None



def explore(var_id: str, unitdef: list):
    variable_list = []
    temp_list = [var for var in unitdef['dlpc']['vars'] if var['id'] == var_id]
    assert len(temp_list) != 0, 'No variables of name: ' + var_id + ' found'
    assert len(temp_list) == 1, "Detected multiple variables with the same name"
    target_variable = temp_list[0]
    if target_variable['type'] == "DV":
        print("This is a DV")
    if target_variable['type'] == "CV":
        print("This is a CV")
    if target_variable['type'] != "VV":
        if target_variable['tag_id'] != "":
            if search_dcs_tags(target_variable['tag_id'], unitdef['dlpc']['streams']):
                variable_list.append(target_variable['tag_id'])
    if target_variable['type'] == "VV":
        try:
            function_text = target_variable['config']['function']
            variable_list = extract_variables(function_text, "('", "',")
        except:
            pass
    formatted_list = [format_var_name(v) for v in variable_list]
    return formatted_list


def format_var_name(var_name: str):
    replaced = "'" + '"'
    formatted = var_name
    for s in replaced:
        formatted = formatted.replace(s, "")
    return formatted


# Press the green button in the gutter to run the script.
unitdef_name = 'limit_def.yml'
variable_id = 'i_37plt_c5_rvp_value'


def initialize_graph(var_list):
    net = nx.Graph()
    for index, v in enumerate(var_list):
        curr_node = index
        label = str(curr_node) + ".) " + v
        net.add_node(curr_node, label=label)
    for i in range(len(var_list) - 1):
        net.add_edge(0, i + 1)

    return net


def modify_graph(var_list, target_node, G):
    net = G
    node_number = net.number_of_nodes()
    listable = [[index, char] for index, char in enumerate(var_list)]
    listable = listable[:][1:len(var_list)]
    for index, v in listable:
        curr_node = index + node_number
        label = str(curr_node) + ".) " + v
        net.add_node(curr_node, label=label)

    for i in range(1, len(var_list)):
        curr_i = i + node_number
        net.add_edge(target_node, curr_i)

    return net

def show()

def str_eql(value, key):
    if len(key) != len(value):
        return False
    flag = False
    for i in range(len(value)):
        if key[i] == value[i] or key[i] == "*":
            flag = True
        else:
            return False
    return flag


if __name__ == '__main__':
    with open(unitdef_name, 'r') as f:
        unitdef = yaml.load(f, Loader=yaml.FullLoader)

    nt = Network('500px', '500px')
    variables = explore(variable_id, unitdef)
    print(variables)
    variable_id = [variable_id]
    variable_id = [*variable_id, *variables]
    print(variable_id)
    G = initialize_graph(variable_id)
    print("Num of nodes:", G.number_of_nodes())
    var_list_2 = explore(variable_id[4], unitdef)
    print(variable_id[4])
    print([variable_id[4], *var_list_2])
    G = modify_graph([variable_id[4], *var_list_2], 4, G)

    print("var list 2", var_list_2[0])
    var_list_3 = explore(var_list_2[0], unitdef)
    node_num = G.number_of_nodes()
    print("node num", node_num)
    G = modify_graph([ "",*var_list_3],node_num,G)
    print(var_list_3)
    nt.from_nx(G)
    nt.show("nx.html")