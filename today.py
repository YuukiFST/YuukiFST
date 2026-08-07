import datetime
from dateutil import relativedelta
import requests
import os
import sys
from lxml import etree
import time
import hashlib
import base64
import io

# Heatmap geometry lives with the layout, not here — importing it keeps the grid
# this script draws aligned with the placeholder the template ships.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))
from build_svg_template import (
    HEAT_CELL,
    HEAT_MONTHS_Y,
    HEAT_PITCH,
    HEAT_WEEKS,
    HEAT_X,
    FUT_W,
)

# Fine-grained personal access token with All Repositories access:
# Account permissions: read:Followers, read:Starring, read:Watching
# Repository permissions: read:Commit statuses, read:Contents, read:Issues, read:Metadata, read:Pull Requests
# Issues and pull requests permissions not needed at the moment, but may be used in the future
HEADERS = {'authorization': 'token '+ os.environ['ACCESS_TOKEN']}
USER_NAME = os.environ['USER_NAME'] # 'Andrew6rant'
# Commit author emails to credit on top of whatever GitHub already links to the
# account — see authored_by_me(). Comma separated, empty by default.
AUTHOR_EMAILS = {email.strip().lower() for email in os.environ.get('AUTHOR_EMAILS', '').split(',') if email.strip()}
QUERY_COUNT = {'user_getter': 0, 'follower_getter': 0, 'graph_repos_stars': 0, 'recursive_loc': 0, 'graph_commits': 0, 'loc_query': 0}


def daily_readme(birthday):
    """
    Returns the length of time since I was born
    e.g. 'XX years, XX months, XX days'
    """
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    return '{} {}, {} {}, {} {}{}'.format(
        diff.years, 'year' + format_plural(diff.years), 
        diff.months, 'month' + format_plural(diff.months), 
        diff.days, 'day' + format_plural(diff.days),
        ' 🎂' if (diff.months == 0 and diff.days == 0) else '')


def format_plural(unit):
    """
    Returns a properly formatted number
    e.g.
    'day' + format_plural(diff.days) == 5
    >>> '5 days'
    'day' + format_plural(diff.days) == 1
    >>> '1 day'
    """
    return 's' if unit != 1 else ''


def simple_request(func_name, query, variables):
    """
    Returns a request, or raises an Exception if the response does not succeed.
    """
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        return request
    raise Exception(func_name, ' has failed with a', request.status_code, request.text, QUERY_COUNT)


def graph_commits(start_date, end_date):
    """
    Uses GitHub's GraphQL v4 API to return my total commit count
    """
    query_count('graph_commits')
    query = '''
    query($start_date: DateTime!, $end_date: DateTime!, $login: String!) {
        user(login: $login) {
            contributionsCollection(from: $start_date, to: $end_date) {
                contributionCalendar {
                    totalContributions
                }
            }
        }
    }'''
    variables = {'start_date': start_date,'end_date': end_date, 'login': USER_NAME}
    request = simple_request(graph_commits.__name__, query, variables)
    return int(request.json()['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'])


def graph_repos_stars(count_type, owner_affiliation, cursor=None, add_loc=0, del_loc=0):
    """
    Uses GitHub's GraphQL v4 API to return my total repository, star, or lines of code count.
    """
    query_count('graph_repos_stars')
    query = '''
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!, $cursor: String) {
        user(login: $login) {
            repositories(first: 100, after: $cursor, ownerAffiliations: $owner_affiliation) {
                totalCount
                edges {
                    node {
                        ... on Repository {
                            nameWithOwner
                            stargazers {
                                totalCount
                            }
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME, 'cursor': cursor}
    request = simple_request(graph_repos_stars.__name__, query, variables)
    if request.status_code == 200:
        if count_type == 'repos':
            return request.json()['data']['user']['repositories']['totalCount']
        elif count_type == 'stars':
            return stars_counter(request.json()['data']['user']['repositories']['edges'])


def recursive_loc(owner, repo_name, data, cache_comment, addition_total=0, deletion_total=0, my_commits=0, cursor=None):
    """
    Uses GitHub's GraphQL v4 API and cursor pagination to fetch 100 commits from a repository at a time
    """
    query_count('recursive_loc')
    query = '''
    query ($repo_name: String!, $owner: String!, $cursor: String) {
        repository(name: $repo_name, owner: $owner) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 100, after: $cursor) {
                            totalCount
                            edges {
                                node {
                                    ... on Commit {
                                        committedDate
                                    }
                                    author {
                                        email
                                        user {
                                            id
                                        }
                                    }
                                    deletions
                                    additions
                                }
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
            }
        }
    }'''
    variables = {'repo_name': repo_name, 'owner': owner, 'cursor': cursor}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS) # I cannot use simple_request(), because I want to save the file before raising Exception
    if request.status_code == 200:
        if request.json()['data']['repository']['defaultBranchRef'] != None: # Only count commits if repo isn't empty
            return loc_counter_one_repo(owner, repo_name, data, cache_comment, request.json()['data']['repository']['defaultBranchRef']['target']['history'], addition_total, deletion_total, my_commits)
        else: return 0
    force_close_file(data, cache_comment) # saves what is currently in the file before this program crashes
    if request.status_code == 403:
        raise Exception('Too many requests in a short amount of time!\nYou\'ve hit the non-documented anti-abuse limit!')
    raise Exception('recursive_loc() has failed with a', request.status_code, request.text, QUERY_COUNT)


def authored_by_me(author):
    """
    True when a commit is mine. GitHub only links a commit to an account when
    the author email is verified on that account, so commits written with an
    unregistered email (an old machine, a bare `Yuuki` with no domain) come back
    with a null user and silently vanish from the count. AUTHOR_EMAILS is the
    escape hatch: any literal author email listed there counts as mine.
    """
    if author is None:
        return False
    if author.get('user') == OWNER_ID:
        return True
    return (author.get('email') or '').lower() in AUTHOR_EMAILS


def loc_counter_one_repo(owner, repo_name, data, cache_comment, history, addition_total, deletion_total, my_commits):
    """
    Recursively call recursive_loc (since GraphQL can only search 100 commits at a time) 
    only adds the LOC value of commits authored by me
    """
    for node in history['edges']:
        if authored_by_me(node['node']['author']):
            my_commits += 1
            addition_total += node['node']['additions']
            deletion_total += node['node']['deletions']

    if history['edges'] == [] or not history['pageInfo']['hasNextPage']:
        return addition_total, deletion_total, my_commits
    else: return recursive_loc(owner, repo_name, data, cache_comment, addition_total, deletion_total, my_commits, history['pageInfo']['endCursor'])


def loc_query(owner_affiliation, comment_size=0, force_cache=False, cursor=None, edges=[]):
    """
    Uses GitHub's GraphQL v4 API to query all the repositories I have access to (with respect to owner_affiliation)
    Queries 60 repos at a time, because larger queries give a 502 timeout error and smaller queries send too many
    requests and also give a 502 error.
    Returns the total number of lines of code in all repositories
    """
    query_count('loc_query')
    query = '''
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!, $cursor: String) {
        user(login: $login) {
            repositories(first: 60, after: $cursor, ownerAffiliations: $owner_affiliation) {
            edges {
                node {
                    ... on Repository {
                        nameWithOwner
                        defaultBranchRef {
                            target {
                                ... on Commit {
                                    history {
                                        totalCount
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME, 'cursor': cursor}
    request = simple_request(loc_query.__name__, query, variables)
    if request.json()['data']['user']['repositories']['pageInfo']['hasNextPage']:   # If repository data has another page
        edges += request.json()['data']['user']['repositories']['edges']            # Add on to the LoC count
        return loc_query(owner_affiliation, comment_size, force_cache, request.json()['data']['user']['repositories']['pageInfo']['endCursor'], edges)
    else:
        return cache_builder(edges + request.json()['data']['user']['repositories']['edges'], comment_size, force_cache)


def cache_builder(edges, comment_size, force_cache, loc_add=0, loc_del=0):
    """
    Checks each repository in edges to see if it has been updated since the last time it was cached
    If it has, run recursive_loc on that repository to update the LOC count
    """
    filename = 'cache/'+hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest()+'.txt' # Create a unique filename for each user
    try:
        with open(filename, 'r') as f:
            stored = f.readlines()
    except FileNotFoundError:
        stored = []

    cache_comment = stored[:comment_size]
    cache_comment += ['This line is a comment block. Write whatever you want here.\n'] * (comment_size - len(cache_comment))

    # Keyed by repo hash, never by line position. GraphQL returns repositories
    # in whatever order it likes, so the old positional lookup let a reorder or
    # a rename knock every line out of alignment — and since the mismatch had no
    # else branch, the affected repos silently kept stale numbers forever.
    known = {}
    for line in stored[comment_size:]:
        fields = line.split()
        if len(fields) == 5:
            known[fields[0]] = fields[1:]

    cached = True # Assume all repositories are cached
    rows = []
    for edge in edges:
        name = edge['node']['nameWithOwner']
        repo_hash = hashlib.sha256(name.encode('utf-8')).hexdigest()
        branch = edge['node']['defaultBranchRef']
        if branch is None: # empty repository, nothing to walk
            rows.append((repo_hash, 0, 0, 0, 0))
            continue
        total_commits = branch['target']['history']['totalCount']
        previous = known.get(repo_hash)
        if previous is not None and not force_cache and int(previous[0]) == total_commits:
            rows.append((repo_hash, total_commits, int(previous[1]), int(previous[2]), int(previous[3])))
            continue
        cached = False
        owner, repo_name = name.split('/')
        loc = recursive_loc(owner, repo_name, serialize_cache(rows), cache_comment)
        additions, deletions, my_commits = (0, 0, 0) if loc == 0 else loc
        rows.append((repo_hash, total_commits, my_commits, additions, deletions))

    with open(filename, 'w') as f:
        f.writelines(cache_comment)
        f.writelines(serialize_cache(rows))
    for repo_hash, total_commits, my_commits, additions, deletions in rows:
        loc_add += additions
        loc_del += deletions
    return [loc_add, loc_del, loc_add - loc_del, cached]


def serialize_cache(rows):
    """
    Renders cache rows back to their on-disk form: one repo per line, as
    `hash total_commits my_commits additions deletions`.
    """
    return [' '.join(str(field) for field in row) + '\n' for row in rows]


def add_archive():
    """
    Repositories I contributed to that no longer exist on GitHub cannot be
    walked by the API, so their last known numbers are kept by hand in
    cache/repository_archive.txt — one repo per line, same shape as the live
    cache (`name total_commits my_commits additions deletions`), `#` for
    comments. Returns [additions, deletions, net, commits, repos]; all zeros
    when the file is absent, which is the normal case.
    """
    try:
        with open('cache/repository_archive.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return [0, 0, 0, 0, 0]
    added_loc, deleted_loc, added_commits, contributed_repos = 0, 0, 0, 0
    for line in lines:
        fields = line.split('#', 1)[0].split()
        if len(fields) != 5:
            continue
        __, __, my_commits, additions, deletions = fields
        added_loc += int(additions)
        deleted_loc += int(deletions)
        added_commits += int(my_commits)
        contributed_repos += 1
    return [added_loc, deleted_loc, added_loc - deleted_loc, added_commits, contributed_repos]

def force_close_file(data, cache_comment):
    """
    Forces the file to close, preserving whatever data was written to it
    This is needed because if this function is called, the program would've crashed before the file is properly saved and closed
    """
    filename = 'cache/'+hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest()+'.txt'
    with open(filename, 'w') as f:
        f.writelines(cache_comment)
        f.writelines(data)
    print('There was an error while writing to the cache file. The file,', filename, 'has had the partial data saved and closed.')


def stars_counter(data):
    """
    Count total stars in repositories owned by me
    """
    total_stars = 0
    for node in data: total_stars += node['node']['stargazers']['totalCount']
    return total_stars


def graph_contribution_calendar():
    """
    Uses GitHub's GraphQL v4 API to return the last 53 weeks of the contribution
    calendar as a list of weeks, each a list of daily counts (Sunday first).
    """
    query_count('graph_commits')
    end_date = datetime.datetime.now(datetime.timezone.utc)
    start_date = end_date - datetime.timedelta(weeks=HEAT_WEEKS)
    query = '''
    query($start_date: DateTime!, $end_date: DateTime!, $login: String!) {
        user(login: $login) {
            contributionsCollection(from: $start_date, to: $end_date) {
                contributionCalendar {
                    weeks {
                        contributionDays {
                            contributionCount
                            date
                        }
                    }
                }
            }
        }
    }'''
    variables = {
        'start_date': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end_date': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'login': USER_NAME,
    }
    request = simple_request(graph_contribution_calendar.__name__, query, variables)
    weeks = request.json()['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    return weeks[-HEAT_WEEKS:]


def heat_level(count, peak):
    """
    Buckets a daily contribution count into one of the 5 heatmap shades
    """
    if count == 0 or peak == 0:
        return 0
    for level, threshold in enumerate((0.25, 0.5, 0.75), start=1):
        if count <= peak * threshold:
            return level
    return 4


def calendar_metrics(weeks):
    """
    Returns (current streak, longest streak, peak day) from the contribution
    calendar. Days are walked oldest first; the streak in progress counts only
    if it reaches the most recent day with activity.
    """
    days = [day for week in weeks for day in week['contributionDays']]
    longest, running = 0, 0
    peak = {'contributionCount': 0, 'date': days[0]['date'] if days else '—'}
    for day in days:
        running = running + 1 if day['contributionCount'] > 0 else 0
        longest = max(longest, running)
        if day['contributionCount'] > peak['contributionCount']:
            peak = day
    # today being quiet does not break a streak that is still alive
    tail = days[:-1] if days and days[-1]['contributionCount'] == 0 else days
    current = 0
    for day in reversed(tail):
        if day['contributionCount'] == 0:
            break
        current += 1
    return current, longest, peak


def gitfut_card():
    """
    Reads gitfut.com, which grades a GitHub account as a FIFA Ultimate Team
    card, and returns {tier, image} where image is the card art cropped out of
    the page's social image as a WebP data URI.
    Returns None if the site is unreachable or its layout moved — the card then
    keeps whatever it was last drawn with instead of blanking out.
    """
    try:
        card = requests.get('https://gitfut.com/api/card/' + USER_NAME, timeout=20)
        card.raise_for_status()
        card = card.json()
        social = requests.get('https://gitfut.com/' + USER_NAME + '/opengraph-image', timeout=30)
        social.raise_for_status()
        return {
            'tier': '{} {} · {}'.format(card['overall'], card['finishLabel'], card['archetype']),
            'image': crop_fut_card(social.content),
        }
    except Exception as error:
        print('   gitfut card:        skipped ({})'.format(error))
        return None


def crop_fut_card(social_png):
    """
    Cuts the card out of gitfut's 1200x630 social image and returns it as a
    WebP data URI at twice the size it is drawn, background knocked out so the
    shield sits on either theme. WebP because the same crop costs 28 kB here
    and 171 kB as PNG, and the file is rewritten on every run.
    """
    from PIL import Image, ImageDraw
    image = Image.open(io.BytesIO(social_png)).convert('RGB')
    pixels = image.load()
    backdrop = pixels[5, 5]
    def differs(x, y):
        return sum(abs(a - b) for a, b in zip(pixels[x, y], backdrop)) > 40
    # the right half of the social image is the marketing copy, not the card
    columns = [x for x in range(500) if any(differs(x, y) for y in range(0, image.height, 2))]
    rows = [y for y in range(image.height) if any(differs(x, y) for x in range(columns[0], columns[-1], 2))]
    card = image.crop((columns[0], rows[0], columns[-1] + 1, rows[-1] + 1)).convert('RGBA')
    for corner in ((0, 0), (card.width - 1, 0), (0, card.height - 1), (card.width - 1, card.height - 1)):
        ImageDraw.floodfill(card, corner, (0, 0, 0, 0), thresh=70)
    card = card.resize((FUT_W * 2, round(FUT_W * 2 * card.height / card.width)), Image.LANCZOS)
    buffer = io.BytesIO()
    card.save(buffer, 'WEBP', quality=88, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buffer.getvalue()).decode()


def fut_overwrite(root, card):
    """
    Drops the card art into its slot and prints the finish under it.
    """
    if card is None:
        return
    art = root.find(".//*[@id='fut_card']")
    if art is not None:
        art.set('href', card['image'])
    # the dashed frame is only there to make an empty slot obvious
    frame = root.find(".//*[@id='fut_frame']")
    if frame is not None:
        frame.getparent().remove(frame)
    find_and_replace(root, 'fut_tier', card['tier'])


def heatmap_overwrite(root, weeks):
    """
    Redraws the contribution grid and its month labels from the real calendar.
    One group per week, so the template's column-by-column wipe still lines up.
    """
    grid = root.find(".//*[@id='heatmap']")
    labels = root.find(".//*[@id='heatmap_months']")
    if grid is None or labels is None:
        return
    peak = max((day['contributionCount'] for week in weeks for day in week['contributionDays']), default=0)

    for child in list(grid):
        grid.remove(child)
    for child in list(labels):
        labels.remove(child)

    for week_index, week in enumerate(weeks):
        column = etree.SubElement(grid, '{http://www.w3.org/2000/svg}g')
        column.set('class', 'reveal hw' + str(week_index))
        for day_index, day in enumerate(week['contributionDays']):
            cell = etree.SubElement(column, '{http://www.w3.org/2000/svg}rect')
            cell.set('class', 'lvl' + str(heat_level(day['contributionCount'], peak)))
            cell.set('x', str(week_index * HEAT_PITCH))
            cell.set('y', str(day_index * HEAT_PITCH))
            cell.set('width', str(HEAT_CELL))
            cell.set('height', str(HEAT_CELL))
            cell.set('rx', '2')

    previous_month = None
    for week_index, week in enumerate(weeks):
        month = datetime.datetime.strptime(week['contributionDays'][0]['date'], '%Y-%m-%d').month
        if month == previous_month:
            continue
        previous_month = month
        label = etree.SubElement(labels, '{http://www.w3.org/2000/svg}tspan')
        label.set('x', str(HEAT_X + week_index * HEAT_PITCH))
        label.set('y', str(HEAT_MONTHS_Y))
        label.text = datetime.date(2000, month, 1).strftime('%b')


def svg_overwrite(filename, age_data, commit_data, loc_data, weeks, card):
    """
    Parse SVG files and update age, commits, lines of code, streak metrics, the
    heatmap.
    loc_data is [added, deleted, net] from loc_query()
    """
    tree = etree.parse(filename)
    root = tree.getroot()
    # the template bakes in its build date; this is the date of the data run
    find_and_replace(root, 'login_date', datetime.datetime.now().strftime('%a %b %d %Y'))
    justify_format(root, 'age_data', age_data)
    justify_format(root, 'commit_data', commit_data)
    justify_format(root, 'loc_data', loc_data[2])
    justify_format(root, 'loc_add', loc_data[0])
    justify_format(root, 'loc_del', loc_data[1])
    current, longest, peak = calendar_metrics(weeks)
    find_and_replace(root, 'streak_data', '{} day{} current  ·  {} longest'.format(
        current, format_plural(current), longest))
    find_and_replace(root, 'peak_data', '{} contributions on {}'.format(
        peak['contributionCount'], peak['date']))
    heatmap_overwrite(root, weeks)
    fut_overwrite(root, card)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


def justify_format(root, element_id, new_text, length=0):
    """
    Updates and formats the text of the element, and modifes the amount of dots in the previous element to justify the new text on the svg
    """
    if isinstance(new_text, int):
        new_text = f"{'{:,}'.format(new_text)}"
    new_text = str(new_text)
    find_and_replace(root, element_id, new_text)
    just_len = max(0, length - len(new_text))
    if just_len <= 2:
        dot_map = {0: '', 1: ' ', 2: '. '}
        dot_string = dot_map[just_len]
    else:
        dot_string = ' ' + ('.' * just_len) + ' '
    find_and_replace(root, f"{element_id}_dots", dot_string)


def find_and_replace(root, element_id, new_text):
    """
    Finds the element in the SVG file and replaces its text with a new value
    """
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        element.text = new_text


def commit_counter(comment_size):
    """
    Counts up my total commits, using the cache file created by cache_builder.
    """
    total_commits = 0
    filename = 'cache/'+hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest()+'.txt' # Use the same filename as cache_builder
    with open(filename, 'r') as f:
        data = f.readlines()
    cache_comment = data[:comment_size] # save the comment block
    data = data[comment_size:] # remove those lines
    for line in data:
        total_commits += int(line.split()[2])
    return total_commits


def user_getter(username):
    """
    Returns the account ID and creation time of the user
    """
    query_count('user_getter')
    query = '''
    query($login: String!){
        user(login: $login) {
            id
            createdAt
        }
    }'''
    variables = {'login': username}
    request = simple_request(user_getter.__name__, query, variables)
    return {'id': request.json()['data']['user']['id']}, request.json()['data']['user']['createdAt']

def follower_getter(username):
    """
    Returns the number of followers of the user
    """
    query_count('follower_getter')
    query = '''
    query($login: String!){
        user(login: $login) {
            followers {
                totalCount
            }
        }
    }'''
    request = simple_request(follower_getter.__name__, query, {'login': username})
    return int(request.json()['data']['user']['followers']['totalCount'])


def query_count(funct_id):
    """
    Counts how many times the GitHub GraphQL API is called
    """
    global QUERY_COUNT
    QUERY_COUNT[funct_id] += 1


def perf_counter(funct, *args):
    """
    Calculates the time it takes for a function to run
    Returns the function result and the time differential
    """
    start = time.perf_counter()
    funct_return = funct(*args)
    return funct_return, time.perf_counter() - start


def formatter(query_type, difference, funct_return=False, whitespace=0):
    """
    Prints a formatted time differential
    Returns formatted result if whitespace is specified, otherwise returns raw result
    """
    print('{:<23}'.format('   ' + query_type + ':'), sep='', end='')
    print('{:>12}'.format('%.4f' % difference + ' s ')) if difference > 1 else print('{:>12}'.format('%.4f' % (difference * 1000) + ' ms'))
    if whitespace:
        return f"{'{:,}'.format(funct_return): <{whitespace}}"
    return funct_return


if __name__ == '__main__':
    """
    Fausto Yuuki (YuukiFST), adapted from Andrew6rant/Andrew6rant
    """
    print('Calculation times:')
    # define global variable for owner ID and calculate user's creation date
    # e.g {'id': 'MDQ6VXNlcjU3MzMxMTM0'} and 2019-11-03T21:15:07Z for username 'Andrew6rant'
    user_data, user_time = perf_counter(user_getter, USER_NAME)
    OWNER_ID, acc_date = user_data
    formatter('account data', user_time)
    account_start = datetime.datetime.fromisoformat(acc_date.replace('Z', '+00:00')).replace(tzinfo=None)
    age_data, age_time = perf_counter(daily_readme, account_start)
    formatter('age calculation', age_time)
    total_loc, loc_time = perf_counter(loc_query, ['OWNER', 'COLLABORATOR', 'ORGANIZATION_MEMBER'], 7)
    formatter('LOC (cached)', loc_time) if total_loc[-1] else formatter('LOC (no cache)', loc_time)
    commit_data, commit_time = perf_counter(commit_counter, 7)
    # Deleted repositories cannot be walked, so their last known numbers are
    # folded back in here; a no-op when the archive file is absent.
    archive_data = add_archive()
    commit_data += archive_data[3]
    total_loc = [total_loc[0] + archive_data[0], total_loc[1] + archive_data[1], total_loc[2] + archive_data[2], total_loc[3]]
    calendar_data, calendar_time = perf_counter(graph_contribution_calendar)
    formatter('contribution calendar', calendar_time)
    card_data, card_time = perf_counter(gitfut_card)
    formatter('gitfut card', card_time)
    svg_overwrite('dark_mode.svg', age_data, commit_data, total_loc[:-1], calendar_data, card_data)
    svg_overwrite('light_mode.svg', age_data, commit_data, total_loc[:-1], calendar_data, card_data)

    # move cursor to override 'Calculation times:' with 'Total function time:' and the total function time, then move cursor back
    print('\033[F\033[F\033[F\033[F',
        '{:<21}'.format('Total function time:'), '{:>11}'.format('%.4f' % (user_time + age_time + loc_time + commit_time)),
        ' s \033[E\033[E\033[E\033[E', sep='')

    print('Total GitHub GraphQL API calls:', '{:>3}'.format(sum(QUERY_COUNT.values())))
    for funct_name, count in QUERY_COUNT.items(): print('{:<28}'.format('   ' + funct_name + ':'), '{:>6}'.format(count))