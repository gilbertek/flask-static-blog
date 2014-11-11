title: The world is calling!
date: 2013-11-10
published: true

Lorem ipsum dolor sit amet, consectetur adipisicing elit. Consequatur voluptates officiis, mollitia laboriosam vitae culpa vero corporis voluptatum iste neque voluptas repellat tempore tempora nisi ex error maiores ab, sunt.

Lorem ipsum dolor sit amet, consectetur adipisicing elit. Perferendis voluptate in distinctio recusandae vel officiis suscipit, laborum odio praesentium et harum similique molestiae accusantium ratione. Enim sint repellat, voluptas tempora.

Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aperiam magni accusamus recusandae, unde rerum aliquam et nihil animi officiis repudiandae architecto, ipsam, alias odio qui. Saepe a, quos vel nobis.w


	:::python
	def datetimeformat(datetime, timeago=True):
	    readable = datetime.strftime('%Y-%m-%d @ %H:%M')
	    if not timeago:
	        return readable
	    iso_format = datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
	    return '<span class=timeago title="%s">%s</span>' % (
	        iso_format,
	        readable
	    )