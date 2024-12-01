from groups.models import Group


def get_groups(data, request):
    """
    Get a list of all the groups associated with the current user
    """
    user_id: int = request.user.id
    groups = list(Group.objects.filter(user_id=user_id).values())

    return {
        'success': True,
        'message': 'Groups fetched successfully',
        'payload':  groups
    }
    
    
def retrive_group(data, request):
    """
    Retrieve a single source by its id
    """
    group = Group.objects.get(id=request.data['group_id'])

    return {
        'success': True,
        'message': 'Group fetched successfully',
        'payload':  group.__dict__
    }
    

def add_group(data, request):
    """
    Add a new group to the database.
    The request data should contain the 'name' key with the group name.
    """ 
    name: str = data['name']
    user_id: int = request.user.id

    # save the source to the database
    source_obj = Group.objects.create(
        name=name,
        user_id=user_id
    )

    return {
        'success': True,
        'message': 'Source added successfully',
        'payload': source_obj.__dict__,
    }
 
 
def edit_group(data, request):
    """
    Edit an existing group by its id.
    """
    group_id = data['group_id']
    name: str = data.get('name')
    user_id: int = request.user.id
    
    updated_dict = {'id': group_id, 'user_id': user_id}
    if group_id:
        updated_dict['name'] = name
    
    # update the source
    source_obj = Group.objects.filter(id=group_id)
    source_obj.update(**updated_dict)
    
    return {
        'success': True,
        'message': 'Source updated successfully',
        'payload': source_obj.first().__dict__,
    }
    
    
def delete_group(data, request):
    """
    Delete an existing group by its id.
    """
    Group.objects.filter(id=request.data['group_id']).delete()
    
    return {
        'success': True,
        'message': 'Group deleted successfully',
    }    
