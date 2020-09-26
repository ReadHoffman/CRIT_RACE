# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:42:37 2020

@author: Read
"""
import math
import random
import numpy as np

#xor
training_dataset = [[[0,1],1], [ [0,0], 0], [[1,0],1],[[1,1],0] ]
inputs,target = training_dataset[0]

class Node:
    def __init__(self,layer_id,node_id,network_part):
        self.layer_id = layer_id
        self.node_id = node_id
        self.bias = None
        self.network_part = network_part
        self.value = random.random()
        self.dactivation = None # squish value
        self.target = None #expected value
        self.error = None # 1/2 * (current value-expected value)**2
        self.derror = None #derivative of node with respect to error function
        self.batch_cost = []
        
    def activation(self,x):
        #activation
        return 1 / (1 + math.exp(-x))
    
    def dactivation(self,x):
        self.dactivation =  self.activation(x)*(1-self.activation(x))
    
    def calculate_error(self):
        self.error = ((self.value-self.target)**2)/2
        
    def derror(self):
        self.derror = self.value-self.target
        
        
        
    
        
        
class Weight:
    def __init__(self,layer_id_start,layer_id_end,node_id_start,node_id_end):
        self.layer_id_start = layer_id_start
        self.layer_id_end = layer_id_end
        self.node_id_start = node_id_start
        self.node_id_end = node_id_end
        self.network_part = 'weight'
        self.value = random.random()
        self.dactivation = None
        self.batch_cost = []
        
## a collection of nodes (but can also include weights despite it not being a hidden layer)
#class Layer:
#    def __init__(self,num_elements,layer_type,layer_id):
#        self.num_elements = num_elements
#        self.layer_type = layer_type
#        self.layer_id = layer_id
#        self.layer = None
#        
#    def create_layer(self):
#        layer = []
#        for i in range(self.num_elements):
#            if self.layer_type == 'weight':
#                layer.append(Weight(self.layer_id,self.layer_id+1,node_id_start,node_id_end))
#            else:
#                layer.append(Node(self.layer_id,i,self.layer_type))
#            
#        self.layer = layer
#            
        
        
class Network:
    # nodes_input_list should be in the format of [input eg 2, hidden eg 5, hidden eg 5, hidden, etc, output eg 2]
    def __init__(self,nodes_input_list,learning_rate=.01):
        self.nodes_input_list = nodes_input_list
        self.learning_rate = learning_rate
        self.network = None
        self.total_error = None
        self.total_error_history = []
        
    def create_nodes(self):
        network = []            
        nodes_input_list_len = len(self.nodes_input_list)
        #create layers of nodes
        for i, num_nodes in enumerate(self.nodes_input_list):
            layer = []
            for j in range(num_nodes):
                if i == 0: network_part = 'input'
                elif i == nodes_input_list_len-1: network_part = 'output'
                else: network_part = 'hidden'
                layer.append(Node(i,j,network_part))
            network.append(layer)

            #create connections between layers (assume fully connected)
            if i==nodes_input_list_len-1: 
                continue
            else:
                weights = []
                num_nodes_next_layer = self.nodes_input_list[i+1]
                for l in range(num_nodes_next_layer): 
                    for k in range(num_nodes):
                        weights.append(Weight(layer_id_start=i,layer_id_end=i+1,node_id_start=k,node_id_end=l))
                network.append(weights)

        self.network = network
        
    def prior_node(self,weight):
        desired_layers = ['input','hidden']
        #search net for layer matching the weight layer start
        for i, layer in enumerate(self.network):
            if layer[0].network_part in desired_layers and layer[0].layer_id==weight.layer_id_start:
                # search layer for node matching weight's node id start
                prior_node = [node for node in layer if node.node_id==weight.node_id_start][0]
        return prior_node
    
    def prior_weights(self,node):
        desired_layers = ['weight']
        #search net for weight layer end matching the node layer
        for i, layer in enumerate(self.network):
            if layer[0].network_part in desired_layers and layer[0].layer_id_end==node.layer_id:
                # search layer for node matching weight's node id start
                prior_weights = [weight.value for weight in layer if weight.node_id_end==node.node_id]
        return prior_weights
                
    def feed_forward(self):
        # calc for each hidden layer and final ouput, we need to calc activation(input*weight)
        desired_layers = ['hidden','output']
        for i, layer in enumerate(self.network):
            #check if layer type is correct for feedforward calcs
            if layer[0].network_part in desired_layers:
                # get layer length so we can reshape output to match
                layer_len = len(layer)
                # get inputs from prior nodes and activate them
                inputs = [node.activation(node.value) for node in self.network[i-2]]
                inputs_len = len(inputs)
                #get weights that connect current layer to prior layer
                weights = [weight.value for weight in self.network[i-1]]
                
                #column of first matrix must equal row of second matrix
                inputs = np.reshape(inputs,(inputs_len,1))
                weights = np.reshape(weights,(layer_len,inputs_len))
                  
                layer_output = np.dot(np.asarray(weights),np.asarray(inputs))
                layer_output = [item for sublist in layer_output for item in sublist]
                #set those layer values equal to dot product output
                
                for j, output_value in enumerate(layer_output):
                    self.network[i][j].value = output_value
                
    def train(self,training_dataset,iterations=10):
        
        iteration = 0
        while iteration<iterations:
            #pick a random training example
            inputs,target = random.choice(training_dataset)
            #x values input
            for i, node in enumerate(self.network[0]):
                node.value = inputs[i]
                
            error_list = []
            #y values output
            for i, node in enumerate(self.network[-1]):
                self.network[-1][i].target = target
                self.network[-1][i].calculate_error()
                error_list.append(self.network[-1][i].error)
            
            self.total_error = sum(error_list)
            #add error to history for graphing later
            self.total_error_history.append(self.total_error)
            
            ### back propagation goes here ###
            
            # how much does each weight effect the total error
            # d E^total/ d weight
            
            ## using chain rule
            #start with last layer, node 0
            #compute the derivative of error with respect to activation
            # error is ((self.target-self.value)**2)/2
            # derivative is value-trainy
            
            #compute derivative of activation with respect to Z  
            ##### dactivation method should be available for every node
            
            #compute derivative of Z with respect to weight
            # Z is h1*w1 + h2*w2 + hn*wn 
            
            network_len = len(self.network)
            for i in range(network_len):
                i = i*-1
                if self.network[i][0].network_part in ['hidden','output']:
                    self.network[i].derror()
                    node.dactivation()
            
            ### end back propagation ###
            iteration+=1
        
                
        
net = Network([2,2,1])
net.create_nodes()
net.feed_forward()
net.train(training_dataset,iterations=10)
print(net.total_error)


# example dot product
#matrix_input_test1 = [[1],[2]]
#matrix_weight_test1 = [[1,2],[3,4],[5,6],[7,8],[9,10]]
#np.dot(matrix_weight_test1,matrix_input_test1)


def backpropagation(self,y, z_s, a_s):
  dw = []  # dC/dW
  db = []  # dC/dB
  deltas = [None] * len(self.weights)  # delta = dC/dZ  known as error for each layer
  # insert the last layer error
  deltas[-1] = ((y-a_s[-1])*(self.getDerivitiveActivationFunction(self.activations[-1]))(z_s[-1]))
  # Perform BackPropagation
  for i in reversed(range(len(deltas)-1)):
    deltas[i] = self.weights[i+1].T.dot(deltas[i+1])*(self.getDerivitiveActivationFunction(self.activations[i])(z_s[i]))        
    batch_size = y.shape[1]
    db = [d.dot(np.ones((batch_size,1)))/float(batch_size) for d in deltas]
    dw = [d.dot(a_s[i].T)/float(batch_size) for i,d in enumerate(deltas)]
    # return the derivitives respect to weight matrix and biases
    return dw, db