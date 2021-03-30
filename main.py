#!/usr/bin/env python
import sys
import json

AWS_POLICY_TYPE = "AWS::IAM::Policy"
AWS_ROLE_TYPE = "AWS::IAM::Role"
AWS_ACCOUNT = "123456789"
CUSTOM_POSTFIX = "CustomPostfix"

def parse_cf(cf_json_string:str)->dict:
    cfd = json.loads(cf_json_string)
    return cfd


def get_resources_by_type(cf_stack:dict, resource_type:str)->set:
    iam_resource = set()
    for resource_name, resource in cf_stack['Resources'].items():
        if resource.get('Type') == resource_type:
            iam_resource.add(resource_name)
    return iam_resource

def remove_resources(cf_stack:dict, resources:set):
    for r in resources:
        cf_stack['Resources'].pop(r, None)

def get_resources_with_for_roles(cf_stack:dict, roles:set)->dict:
    roles_resrouces = {}
    for resource_name, resource in cf_stack['Resources'].items(): 
        if resource.get("Properties") and 'Role' in resource.get("Properties"):
            for fn, role in resource.get("Properties").get("Role").items():
                if resource_name not in roles_resrouces:
                    roles_resrouces[resource_name] = [role]
                else:
                    roles_resrouces[resource_name].append(role)
        if resource.get("Properties") and 'Roles' in resource.get("Properties"):
            for role in resource.get("Properties").get("Roles"):
                if resource_name not in roles_resrouces:
                    roles_resrouces[resource_name] = [[role.get('Ref'),'Ref']]
                else:
                    roles_resrouces[resource_name].append([[role.get('Ref'),'Ref']])
    return roles_resrouces

def harcode_roles_on_resources(resources:dict, cf_stack:dict):
    prefix_arn = f"arn:aws:iam::{AWS_ACCOUNT}:role/"
    for resource_name, roles in resources.items():
        for role in roles:
            if role[1]=='Arn':
                cf_stack['Resources'][resource_name]['Properties']['Role'] = prefix_arn + role[0] + CUSTOM_POSTFIX
            elif role[1]=="Ref":
                cf_stack['Resources'][resource_name]['Properties'].pop('Roles', None)
                cf_stack['Resources'][resource_name]['Properties']['Role'] = prefix_arn + role[0] + CUSTOM_POSTFIX
                   
def main():
    cloud_formation_stack = parse_cf(sys.stdin.read())
    policies_to_remove = get_resources_by_type(cloud_formation_stack, AWS_POLICY_TYPE)
    # print(f'Policies to remove: {policies_to_remove}.')
    remove_resources(cloud_formation_stack, policies_to_remove)
    # print(cloud_formation_stack)
    roles_to_hardcode = get_resources_by_type(cloud_formation_stack, AWS_ROLE_TYPE)
    remove_resources(cloud_formation_stack, roles_to_hardcode)
    # print(f'Roles to change: {roles_to_hardcode}')
    resource_to_change = get_resources_with_for_roles(cloud_formation_stack, roles_to_hardcode)
    harcode_roles_on_resources(resource_to_change, cloud_formation_stack)
    print(json.dumps(cloud_formation_stack))

main()

# cf_stack = parse_cf(sys.stdin.read())
# for resource_name, resource in cf_stack['Resources'].items(): 
    # if resource.get("Properties") and 'Role' in resource.get("Properties"):
        # print(resource.get("Properties").get("Role"))
