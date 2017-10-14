from lxml import html
import requests

class Item(object):
    def __init__(self):
        self.id = ""
        self.content = ""
        self.user = ""
        self.time = ""
        self.depth = 0
        self.parent = None
        self.children = []

    def print(self):
        print(" "*self.depth + self.id)
        for child in self.children:
            child.print()

class Head(object):
    item = Item
    created = ""

    def __init__(self, item, created):
        self.item = item
        self.created = created

def get_items():
    # Get website page
    article_id = "15473719"

    website = "https://news.ycombinator.com/item?id=" + article_id

    page = requests.get(website)
    tree = html.fromstring(page.content)

    # Collect top item
    ## Collect user
    ## Depth of 0
    ## No parent
    head_title_xpath = "//*[@id=\"{}\"]/td[3]/a/text()".format(article_id)
    head_title = tree.xpath(head_title_xpath)[0]
    user_xpath = "//*[contains(@class,'hnuser')]/text()"
    head_user = tree.xpath(user_xpath)[0]
    head_time_xpath = "//span[contains(@class,'age')]/a"
    head_time = tree.xpath(head_time_xpath)[0].text

    # For all depths of comments, collect comments
    comments_xpath = "//*[contains(@class,'comtr')]"
    comments = tree.xpath(comments_xpath)

    head = Item()
    head.id = article_id
    head.content = head_title
    head.user = head_user
    # TODO: Get this working
    head.time = ""

    last_item = head
    last_depth = 0

    comment_trailer = "\n                      \n                      reply\n                  \n      "

    for comment in comments:
        ## Collect user
        item = Item()
        item.id = comment.attrib['id']
        item.user = comment.xpath("."+user_xpath)[0]

        content_xpath = ".//*[contains(@class,'comment')]"
        content_container = comment.xpath(content_xpath)[0]
        span = content_container.getchildren()[0]
        item.content = span.text_content()[:-len(comment_trailer)]

        age_xpath = "."+head_time_xpath
        item.time = comment.xpath(age_xpath)[0].text

        depth_xpath = ".//*[contains(@class, 'ind')]/img"
        depth = comment.xpath(depth_xpath)[0].attrib['width']
        depth = int(depth) // 40
        depth += 1

        item.depth = depth

        if depth > last_depth: # Depth increase 1
            # This is a child comment
            parent = last_item

        elif depth == last_depth: # Depth hasn't changed
            parent = last_item.parent
        else:
            # Depth decreases by last_depth - depth
            # i.e. 6 now 4, therefore a change by 2
            # Walk up the tree for each
            depth_diff = last_item.depth - item.depth
            parent = last_item
            for _ in range(1, depth_diff):
                parent = parent.parent

        parent.children.append(item)
        item.parent = parent
        last_item = item
        last_depth = last_item.depth

    return head

def main():
    i = get_items()
    i.print()

if __name__ == "__main__":
    main()