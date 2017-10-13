# Switch~ Ensemble Website

This README serves as documentation for how the Switch~ Ensemble website is structured and for updating it in the future in case there's a time when Chris or Jason are not actively updating it.

This website is built upon a template that uses the [Bootstrap][BS4 website] toolkit, and the site is hosted on GitHub pages and built with GitHub's [Jekyll][Jekyll website] static site generator. Jekyll relies extensively on the [Liquid][Liquid Github] templating engine, which facilitates developing sites through templates and scripting. Hopefully, this website is setup in such a way that it is easy to update even if you have no background in web development. But knowing a bit about Jekyll, Liquid, and YAML will definitely be helpful. You can find out more about these and other things here:

- [Bootstrap][Bootstrap documentation] is the framework at the foundation of the site's template. Read more about Bootstrap at the link.
- [Markdown][Markdown cheatsheet] is a simple and direct markup language great for easily writing and outputting HTML. It has been around for a while and is widely supported on a number of websites.
- The [Jekyll documentation webpage][Jekyll documentation] contains a lot of information about what Jekyll is, how it works, and how it makes use of Liquid and YAML front matter.
- [YAML][YAML overview] stands for YAML Ain't Markup Language. It is a "human friendly data serialization standard for all programming languages." It is essential to taking advantage of Jekyll's templating features and makes modifying page elements easy. Read more about Jekyll's usage of it [here][Jekyll front matter].
- An overview of the [Liquid templating engine syntax][Liquid syntax] can be found at the link.

Below are the various elements of the site, where they can be found, and how they can be edited and modified.

# Global Elements

Liquid's templating language allows you to have any number of page layouts, which can be found in the `_layouts` folder. Most of the layouts inherit their structure from the `default.html` layout, which contains the most important global elements. These are standard HTML elements that are found on each and every page. Each of these global elements are loaded from in `default.html` layout and can be found in the `_includes` folder.

- `head.html` contains global information about website, including favicons, page title listed in tabs, fonts, and css. Javascript files, which are sometimes found in the `head`, are located at the bottom of the page to make the site load faster.
- `header.html` contains the navigation bar found at the top of the page.

  - The actual link listings and submenus are automatically created and loaded from the file `navigation.yml` which is found in the `_data` folder.
  - To add new links to new pages or change existing links, go to the `navigation.yml` file and follow the YAML format found there.
  - The links will appear in the navigation bar in the order that they are listed in the `navigation.yml` file.

- `footer.html` contains the last content area found at the bottom of every page.

  - Currently it contains contact information, links to various social media sites, and listings of upcoming recent performances and latest news.
  - These listings are automatically updated when new posts are added to the `_posts` folder. The YAML front matter of the posts in this folder contain a mapping for categories (e.g., category: news). When the post category contains "performance" or "news", then it will be listed in this footer area.
  - The appearance of the listings can be changed by editing the `home-latest-news.html` and `home-latest-performances.html` files found in the `_includes` folder.

- `scripts.html` contains Javascript files necessary for the site to function and display things properly.

# Individual Pages

Coming soon.

[BS4 website]: https://getbootstrap.com/
[Bootstrap documentation]: https://getbootstrap.com/docs/4.0/getting-started/introduction/
[Markdown cheatsheet]: https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet
[Jekyll website]: https://jekyllrb.com/
[Jekyll documentation]: https://jekyllrb.com/docs/home/
[Jekyll front matter]: https://jekyllrb.com/docs/frontmatter/
[Liquid Github]: https://github.com/Shopify/liquid
[Liquid syntax]: https://shopify.github.io/liquid/
[YAML overview]: https://learn.getgrav.org/advanced/yaml
