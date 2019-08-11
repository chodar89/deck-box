colors = mongo.db.colors.find()
    card_rarity = mongo.db.rarity.find()
    expansion = mongo.db.expansion_set.find()
    card_types = mongo.db.card_types.find()
    rating = mongo.db.rating.find()
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    user_name = session['userinfo'].get("username")
    user = mongo.db.users.find_one({"username": user_name})
    user_id = ObjectId(session['userinfo'].get("id"))
    if request.method == "POST":
        # If method is POST take number of cards to display from form
        change_per_page = request.form.get('change_per_page')
        mongo.db.users.update({'username': user_name},
                              {'$set': {'user_per_page':change_per_page}},
                              multi=False)
        if request.form.get('color') is None:
            return redirect(url_for('my_cards'))
        else:
            session['filter'] = {
                'color': request.form.getlist('color'),
                'type': request.form.getlist('type'),
                'rarity': request.form.getlist('rarity'),
                'sort_by': request.form.get('sort_by'),
                'descending_ascending': request.form.get('descending_ascending')
            }
            return redirect(url_for('my_cards'))
    per_page = int(user['user_per_page'])
    card_output = []
    if 'filter' not in session:
        cards = mongo.db.cards.find({
                'user_id': user_id}).sort('_id', pymongo.DESCENDING).skip(
                (page - 1) * per_page).limit(per_page)
    else:
        def get_objectid_for_category(session_filter, container):
            """Get _id for each category from session['filter'] and append ObjectId"""
            for each in session_filter:
                container.append(ObjectId(each))
        types_filter = []
        rarity_filter = []
        color_filter = []
        sort_by = session['filter'].get('sort_by')
        descending_ascending = session['filter'].get('descending_ascending')
        if descending_ascending == 'descending':
            pymongo_sort = pymongo.DESCENDING
        else:
            pymongo_sort = pymongo.ASCENDING
        get_objectid_for_category(session['filter'].get('color'), color_filter)
        get_objectid_for_category(session['filter'].get('type'), types_filter)
        get_objectid_for_category(session['filter'].get('rarity'), rarity_filter)
        cards = mongo.db.cards.find({
            '$and': [{'user_id': user_id},
                     {'color': {'$in': color_filter}},
                     {'type': {'$in': types_filter}},
                     {'rarity': {'$in': rarity_filter}},
                     ]}).sort(sort_by, pymongo_sort).skip(
                (page - 1) * per_page).limit(per_page)
    for card in cards:
        card_output.append(card)
    if cards is None:
        count_user_cards = 0
        flash('you do not have any cards in your collection yet', 'error')
    else:
        count_user_cards = cards.count()
    pagination = Pagination(page=page, per_page=per_page, total=count_user_cards,
                            search=search, record_name='card_output')
    return render_template('cards.html', card_output=card_output,
                           pagination=pagination, per_page=per_page,
                           colors=colors, card_types=card_types, card_rarity=card_rarity)