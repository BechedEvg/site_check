# site_check
"site_check" script for collecting site data according to SEO requirements.

The script requires the presence in the directory of the file "google_result.json" which is the result of the script "google_parser".

Having received the site url, the script collects the list of site links indexed by google from the "google_result.json" file and combines them with the list of links from the sitemap, forming the most complete list of all site pages.

Next, data is collected from the pages from the list.

To find and collect all links to sitemap pages from the sitemap, use ultimate-sitemap-parser 0.5, installation command: pip install ultimate-sitemap-parser.


The result of the script execution is the file "check_result.json".
