# Wp-Rest-Api - Rest-Api

**Pages:** 60

---

## Pagination

**URL:** https://developer.wordpress.org/rest-api/using-the-rest-api/pagination

**Contents:**
- Pagination
- In this article
- Pagination Parameters
- Ordering Results

WordPress sites can have a lot of content—far more than you’d want to pull down in a single request. The API endpoints default to providing a limited number of items per request, the same way that a WordPress site will default to 10 posts per page in archive views.

Any API response which contains multiple resources supports several common query parameters to handle paging through the response data:

Large queries can hurt site performance, so per_page is capped at 100 records. If you wish to retrieve more than 100 records, for example to build a client-side list of all available categories, you may make multiple API requests and combine the results within your application.

To determine how many pages of data are available, the API returns two header fields with every paginated response:

By inspecting these header fields you can determine how much more data is available within the API.

In addition to the pagination query parameters detailed above, several other parameters control the order of the returned results:

Improve it on GitHub: Pagination

See list of changes: Pagination

---

## Posts

**URL:** https://developer.wordpress.org/rest-api/reference/posts

**Contents:**
- Posts
- In this article
- Schema
- List Posts
  - Definition
  - Example Request
  - Arguments
- Create a Post
  - Arguments
  - Definition

The schema defines all the fields that exist within a post record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string or null, Format: datetime (details)

Context: view, edit, embed

JSON data type: string or null, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: string

Context: view, edit, embed

JSON data type: string

One of: publish, future, draft, pending, private

JSON data type: string

Context: view, edit, embed

JSON data type: string

JSON data type: string

JSON data type: string

JSON data type: object

Context: view, edit, embed

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: string

JSON data type: string

JSON data type: string

One of: standard, aside, chat, gallery, link, image, quote, status, video, audio

JSON data type: object

JSON data type: boolean

JSON data type: string

JSON data type: array

JSON data type: array

Query this endpoint to retrieve a collection of posts. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/posts

One of: view, embed, edit

One of: author, date, id, include, modified, parent, relevance, slug, include_slugs, title

GET /wp/v2/posts/<id>

Query this endpoint to retrieve a specific post record.

$ curl https://example.com/wp-json/wp/v2/posts/<id>

One of: view, embed, edit

POST /wp/v2/posts/<id>

$ curl -X POST https://example.com/wp-json/wp/v2/posts/<id> -d '{"title":"My New Title"}'

DELETE /wp/v2/posts/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/posts/<id>

Improve it on GitHub: Posts

See list of changes: Posts

---

## Template_Part Revisions

**URL:** https://developer.wordpress.org/rest-api/reference/wp_template_part-revisions

**Contents:**
- Template_Part Revisions
- In this article
- Schema
- List Template_Part Revisions
  - Definition
  - Example Request
  - Arguments
- Retrieve a Template_Part Revision
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a template_part revision record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object or string

Context: embed, view, edit

JSON data type: object or string

Context: embed, view, edit

Query this endpoint to retrieve a collection of template_part revisions. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/template-parts/<parent>/revisions

$ curl https://example.com/wp-json/wp/v2/template-parts/<parent>/revisions

One of: view, embed, edit

One of: date, id, include, relevance, slug, include_slugs, title

GET /wp/v2/template-parts/<parent>/revisions/<id>

Query this endpoint to retrieve a specific template_part revision record.

$ curl https://example.com/wp-json/wp/v2/template-parts/<parent>/revisions/<id>

One of: view, embed, edit

DELETE /wp/v2/template-parts/<parent>/revisions/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/template-parts/<parent>/revisions/<id>

GET /wp/v2/template-parts/<id>/autosaves

Query this endpoint to retrieve a specific template_part revision record.

$ curl https://example.com/wp-json/wp/v2/template-parts/<id>/autosaves

One of: view, embed, edit

POST /wp/v2/template-parts/<id>/autosaves

GET /wp/v2/template-parts/<parent>/autosaves/<id>

Query this endpoint to retrieve a specific template_part revision record.

$ curl https://example.com/wp-json/wp/v2/template-parts/<parent>/autosaves/<id>

One of: view, embed, edit

Improve it on GitHub: Template_Part Revisions

See list of changes: Template_Part Revisions

---

## Global Parameters

**URL:** https://developer.wordpress.org/rest-api/using-the-rest-api/global-parameters

**Contents:**
- Global Parameters
- In this article
- _fields
- _embed
- _method (or X-HTTP-Method-Override header)
- _envelope
- _jsonp

The API includes a number of global parameters (also called “meta-parameters”) which control how the API handles the request/response handling. These operate at a layer above the actual resources themselves, and are available on all resources.

A REST resource like a Post contains a large quantity of data: basic information such as content, title, and author ID, but also registered metadata and fields, media information, and links to other resources. Your application may not need all of this information on every request.

To instruct WordPress to return only a subset of the fields in a response, you may use the _fields query parameter. If for example you are building an archive view and only need the ID, title, permalink, author and excerpt for a collection of posts, you can restrict the response to only those properties with this fields query:

You may alternatively provide that same list using query parameter array syntax instead of a comma-separated list:

When _fields is provided then WordPress will skip unneeded fields when generating your response object, avoiding potentially expensive internal computation or queries for data you don’t need. This also means the JSON object returned from the REST API will be smaller, requiring less time to download and less time to parse on your client device.

Carefully design your queries to pull in only the needed properties from each resource to make your application faster to use and more efficient to run.

As of WordPress 5.3 the _fields parameter supports nested properties. This can be useful if you have registered many meta keys, permitting you to request the value for only one of the registered meta properties:

Only the meta value with the key one-of-many-keys will be returned, and others will be excluded.

You can also request specific deeply-nested properties within a complex meta object:

Most resources include links to related resources. For example, a post can link to the parent post, or to comments on the post. To reduce the number of HTTP requests required, clients may wish to fetch a resource as well as the linked resources. The _embed parameter indicates to the server that the response should include these embedded resources.

Embed mode is enabled if the _embed parameter is passed in the query string (GET parameter). This parameter does not require a value (i.e. ?_embed is valid), however can be passed “1” as a value if required by a client library.

As of WordPress 5.4, the resources to embed can 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
/wp/v2/posts?_fields=author,id,excerpt,title,link
```

Example 2 (unknown):
```unknown
/wp/v2/posts?_fields[]=author&_fields[]=id&_fields[]=excerpt&_fields[]=title&_fields[]=link
```

Example 3 (unknown):
```unknown
?_fields=meta.one-of-many-keys
```

Example 4 (unknown):
```unknown
?_fields=meta.key_name.nested_prop.deeply_nested_prop,meta.key_name.other_nested_prop
```

---

## Block Pattern Categories

**URL:** https://developer.wordpress.org/rest-api/reference/block-pattern-categories

**Contents:**
- Block Pattern Categories
- In this article
- Schema
- Retrieve a Block Pattern Category
  - Definition & Example Request

The schema defines all the fields that exist within a block pattern category record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

GET /wp/v2/block-patterns/categories

Query this endpoint to retrieve a specific block pattern category record.

$ curl https://example.com/wp-json/wp/v2/block-patterns/categories

Improve it on GitHub: Block Pattern Categories

See list of changes: Block Pattern Categories

---

## Discovery

**URL:** https://developer.wordpress.org/rest-api/using-the-rest-api/discovery

**Contents:**
- Discovery
- In this article
- Discovering the API
  - Link Header
  - Element
  - RSD (Really Simple Discovery)
- Authentication Discovery
- Extension Discovery
- Resource Discovery

When your client talks to an unknown site, you’ll need to discover what the site is capable of and how the site is configured. There are a couple of steps for this, depending on what you need to discover.

The first step of connecting to a site is finding out whether the site has the API enabled. Typically, you’ll be working with URLs from user input, so the site you’re accessing could be anything. The discovery step lets you verify the API is available, as well as indicating how to access it.

The preferred way to handle discovery is to send a HEAD request to the supplied address. The REST API automatically adds a Link header to all front-end pages that looks like the following:

This URL points to the root route (/) of the API, which is then used for further discovery steps.

For sites without “pretty permalinks” enabled, /wp-json/ isn’t automatically handled by WordPress. This means that normal/default WordPress permalinks will be used instead. These headers look more like this:

Clients should keep this variation in mind and ensure that both routes can be handled seamlessly.

This auto-discovery can be applied to any URL served by a WordPress installation, so no pre-processing on user input needs to be added. Since this is a HEAD request, the request should be safe to send blindly to servers without worrying about causing side-effects.

For clients with a HTML parser, or running in the browser, the equivalent of the Link header is included in the <head> of front-end pages through a <link> element:

In-browser Javascript can access this via the DOM:

For in-browser clients, or clients without access to HTTP headers, this may be a more usable way of discovering the API. This is similar to Atom/RSS feed discovery, so existing code for that purpose may also be automatically adapted instead.

For clients with support for XML-RPC discovery, the RSD method may be more applicable. This is an XML-based discovery format typically used for XML-RPC. RSD has two steps. The first step is to find the RSD endpoint, supplied as a <link> element:

The second step is to fetch the RSD document and parse the available endpoints. This involves using an XML parser on a document like the following:

The REST API always has a name attribute with the value equal to WP-API.

RSD is the least-preferred method of autodiscovery for a couple of reasons. The first step of RSD-based discovery involves parsing the HTML to first find the RSD document itself, which is equivalent to the <

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
Link: <http://example.com/wp-json/>; rel="https://api.w.org/"
```

Example 2 (unknown):
```unknown
Link: <http://example.com/?rest_route=/>; rel="https://api.w.org/"
```

Example 3 (unknown):
```unknown
<link rel='https://api.w.org/' href='http://example.com/wp-json/' />
```

Example 4 (js):
```js
// jQuery method
var $link = jQuery( 'link[rel="https://api.w.org/"]' );
var api_root = $link.attr( 'href' );

// Native method
var links = document.getElementsByTagName( 'link' );
var link = Array.prototype.filter.call( links, function ( item ) {
    return ( item.rel === 'https://api.w.org/' );
} );
var api_root = link[0].href;
```

---

## Routes and Endpoints

**URL:** https://developer.wordpress.org/rest-api/extending-the-rest-api/routes-and-endpoints

**Contents:**
- Routes and Endpoints
- In this article
- Overview
- Routes vs Endpoints
- Creating Endpoints
- Routes
  - Namespaces
  - Resource Paths
  - Path Variables
- Endpoints

The REST API provides us a way to match URIs to various resources in our WordPress install. By default, if you have pretty permalinks enabled, the WordPress REST API “lives” at /wp-json/. At our WordPress site https://ourawesomesite.com`, we can access the REST API's index by making aGETrequest tohttps://ourawesomesite.com/wp-json/`. The index provides information regarding what routes are available for that particular WordPress install, along with what HTTP methods are supported and what endpoints are registered.

Endpoints are functions available through the API. This can be things like retrieving the API index, updating a post, or deleting a comment. Endpoints perform a specific function, taking some number of parameters and return data to the client.

A route is the “name” you use to access endpoints, used in the URL. A route can have multiple endpoints associated with it, and which is used depends on the HTTP verb.

For example, with the URL `http://example.com/wp-json/wp/v2/posts/123`:

On sites without pretty permalinks, the route is instead added to the URL as the rest_route parameter. For the above example, the full URL would then be http://example.com/?rest_route=/wp/v2/posts/123

If we wanted to create an endpoint that would return the phrase “Hello World, this is the WordPress REST API” when it receives a GET request, we would first need to register the route for that endpoint. To register routes you should use the register_rest_route() function. It needs to be called on the rest_api_init action hook. register_rest_route() handles all of the mapping for routes to endpoints. Let’s try to create a “Hello World, this is the WordPress REST API” route.

The first argument passed into register_rest_route() is the namespace, which provides us a way to group our routes. The second argument passed in is the resource path, or resource base. For our example, the resource we are retrieving is the “Hello World, this is the WordPress REST API” phrase. The third argument is an array of options. We specify what methods the endpoint can use and what callback should happen when the endpoint is matched (more things can be done but these are the fundamentals).

The third argument also allows us to provide a permissions callback, which can restrict access for the endpoint to only certain users. The third argument also offers a way to register arguments for the endpoint so that requests can modify the response of our endpoint. We will get into those concepts in the 

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
/**
 * This is our callback function that embeds our phrase in a WP_REST_Response
 */
function prefix_get_endpoint_phrase() {
    // rest_ensure_response() wraps the data we want to return into a WP_REST_Response, and ensures it will be properly returned.
    return rest_ensure_response( 'Hello World, this is the WordPress REST API' );
}

/**
 * This function is where we register our routes for our example endpoint.
 */
function prefix_register_example_routes() {
    // register_rest_route() handles more arguments but we are going to stick to the basics for now.
    register_rest_route( 'hello
...
```

Example 2 (php):
```php
/**
 * This is our callback function to return our products.
 *
 * @param WP_REST_Request $request This function accepts a rest request to process data.
 */
function prefix_get_products( $request ) {
    // In practice this function would fetch the desired data. Here we are just making stuff up.
    $products = array(
        '1' => 'I am product 1',
        '2' => 'I am product 2',
        '3' => 'I am product 3',
    );

    return rest_ensure_response( $products );
}

/**
 * This is our callback function to return a single product.
 *
 * @param WP_REST_Request $request This function accepts
...
```

Example 3 (php):
```php
/**
 * This is our callback function to return our products.
 *
 * @param WP_REST_Request $request This function accepts a rest request to process data.
 */
function prefix_get_products( $request ) {
    // In practice this function would fetch the desired data. Here we are just making stuff up.
    $products = array(
        '1' => 'I am product 1',
        '2' => 'I am product 2',
        '3' => 'I am product 3',
    );

    return rest_ensure_response( $products );
}

/**
 * This is our callback function to return a single product.
 *
 * @param WP_REST_Request $request This function accepts
...
```

Example 4 (php):
```php
/**
 * This is our callback function that embeds our resource in a WP_REST_Response
 */
function prefix_get_private_data() {
    // rest_ensure_response() wraps the data we want to return into a WP_REST_Response, and ensures it will be properly returned.
    return rest_ensure_response( 'This is private data.' );
}

/**
 * This is our callback function that embeds our resource in a WP_REST_Response
 */
function prefix_get_private_data_permissions_check() {
    // Restrict endpoint to only users who have the edit_posts capability.
    if ( ! current_user_can( 'edit_posts' ) ) {
        return n
...
```

---

## Requests

**URL:** https://developer.wordpress.org/rest-api/requests

**Contents:**
- Requests
- In this article
- Overview
- WP_REST_Request
- Request Properties
  - Method
  - Route
  - Headers
  - Parameters
    - URL Params

While the WordPress REST API may be called internally within other WordPress code via PHP, the REST API is designed to be used remotely over HTTP. HTTP is the foundation for communication of data over the internet, and any application capable of HTTP requests may make use of the WordPress REST API, whether that application is a client-side JavaScript interface or an application on a remote server running in Python or Java.

The data structure of a request is conveniently handled by the WP_REST_Request class.

This class is one of the three main infrastructure classes introduced in WordPress 4.4. When an HTTP request is made to an endpoint of the API, the API will automatically create an instance of the WP_REST_Request class, matching the provided data. The response object is auto-generated in WP_REST_Server‘s serve_request() method. Once the request is created and authentication is checked, the request is dispatched and our endpoint callbacks begin to be fired. All of the data stored up in the WP_REST_Request object is passed into our callbacks for our registered endpoints. So both our permission_callback and callback are called with the request object being passed in. This enables us to access the various request properties in our callbacks, so that we can tailor our responses to match the desired output.

Request objects have many different properties, each of which can be used in various ways. The main properties are the request method, route, headers, parameters and attributes. Let’s break each of these down into their role in a request. If you were to create a request object yourself it would look like this:

In the above code sample we are only specifying that the request object method is GET and we should be matching the route /my-namespace/v1/examples which in the context of an entire URL would look like this: https://ourawesomesite.com/wp-json/my-namespace/v1/examples`. The method and route arguments for theWP_REST_Request` constructor are used to map the request to the desired endpoint. If the request is made to an endpoint that is not registered then a helpful 404 error message is returned in the response. Let’s look at the various properties in more depth.

The method property of a request object by default matches the HTTP Request method. The method in most cases will be one of GET, POST, PUT, DELETE, OPTIONS, or HEAD. These methods will be used to match the various endpoints registered to a route. When the API finds a match for the method and

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
$request = new WP_REST_Request( 'GET', '/my-namespace/v1/examples' );
```

Example 2 (php):
```php
// Register our individual books endpoint.
function prefix_register_book_route() {
    register_rest_route( 'my-namespace/v1', '/books/(?P<id>\d+)', array(
        // Supported methods for this endpoint. WP_REST_Server::READABLE translates to GET.
        'methods' => WP_REST_Server::READABLE,
        // Register the callback for the endpoint.
        'callback' => 'prefix_get_book',
    ) );
}

add_action( 'rest_api_init', 'prefix_register_book_route' );

/**
 * Our registered endpoint callback. Notice how we are passing in $request as an argument.
 * By default, the WP_REST_Server will pass 
...
```

Example 3 (js):
```js
{
  "methods": {
    "GET": true
  },
  "accept_json": false,
  "accept_raw": false,
  "show_in_index": true,
  "args": {
    "context": {
      "description": "Scope under which the request is made; determines fields present in response.",
      "type": "string",
      "sanitize_callback": "sanitize_key",
      "validate_callback": "rest_validate_request_arg",
      "enum": [
        "view",
        "embed",
        "edit"
      ],
      "default": "view"
    },
    "page": {
      "description": "Current page of the collection.",
      "type": "integer",
      "default": 1,
      "sanitize_c
...
```

Example 4 (php):
```php
// Register our mock batch endpoint.
function prefix_register_batch_route() {
    register_rest_route( 'my-namespace/v1', '/batch', array(
        // Supported methods for this endpoint. WP_REST_Server::READABLE translates to GET.
        'methods' => WP_REST_Server::READABLE,
        // Register the callback for the endpoint.
        'callback' => 'prefix_do_batch_request',
        // Register args for the batch endpoint.
        'args' => prefix_batch_request_parameters(),
    ) );
}

add_action( 'rest_api_init', 'prefix_register_batch_route' );

/**
 * Our registered endpoint callback. Noti
...
```

---

## Menu Locations

**URL:** https://developer.wordpress.org/rest-api/reference/menu-locations

**Contents:**
- Menu Locations
- In this article
- Schema
- Retrieve a Menu Location
  - Definition & Example Request
  - Arguments
- Retrieve a Menu Location
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a menu location record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: integer

Context: embed, view, edit

GET /wp/v2/menu-locations

Query this endpoint to retrieve a specific menu location record.

$ curl https://example.com/wp-json/wp/v2/menu-locations

One of: view, embed, edit

GET /wp/v2/menu-locations/<location>

Query this endpoint to retrieve a specific menu location record.

$ curl https://example.com/wp-json/wp/v2/menu-locations/<location>

One of: view, embed, edit

Improve it on GitHub: Menu Locations

See list of changes: Menu Locations

---

## Adding Custom Endpoints

**URL:** https://developer.wordpress.org/rest-api/extending-the-rest-api/adding-custom-endpoints

**Contents:**
- Adding Custom Endpoints
- In this article
- Bare Basics
  - Namespacing
  - Arguments
  - Return Value
  - Permissions Callback
  - Discovery
- The Controller Pattern
- Examples

The WordPress REST API is more than just a set of default routes. It is also a tool for creating custom routes and endpoints. The WordPress front-end provides a default set of URL mappings, but the tools used to create them (e.g. the Rewrites API, as well as the query classes: WP_Query, WP_User, etc) are also available for creating your own URL mappings, or custom queries.

This document details how to create a new and completely custom route with its own endpoints. We’ll first work through a short example and then expand it out to the full controller pattern as used internally.

So you want to add custom endpoints to the API? Fantastic! Let’s get started with a simple example. Let’s start with a simple function that looks like this:

To make this available via the API, we need to register a route. This tells the API to respond to a given request with our function. We do this through a function called register_rest_route, which should be called in a callback on rest_api_init to avoid doing extra work when the API isn’t loaded.

We need to pass in three things to register_rest_route: the namespace, the route we want, and the options. We’ll come back to the namespace in a bit, but for now, let’s pick myplugin/v1. We’re going to have the route match anything with /author/{id}, where {id} is an integer.

Right now, we’re only registering the one endpoint for the route. The term “route” refers to the URL, whereas “endpoint” refers to the function behind it that corresponds to a method and a URL (for more information, see the Glossary).

For example, if your site domain is example.com and you’ve kept the API path of wp-json, then the full URL would be `http://example.com/wp-json/myplugin/v1/author/(?P\d+)`.

On sites without pretty permalinks, the route is instead added to the URL as the rest_route parameter. For the above example, the full URL would then be http://example.com/?rest_route=/myplugin/v1/author/(?P\d+)

Each route can have any number of endpoints, and for each endpoint, you can define the HTTP methods allowed, a callback function for responding to the request and a permissions callback for creating custom permissions. In addition you can define allowed fields in the request and for each field specify a default value, a sanitization callback, a validation callback, and whether the field is required.

Namespaces are the first part of the URL for the endpoint. They should be used as a vendor/package prefix to prevent clashes between custom routes. Nam

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
<?php
/**
 * Grab latest post title by an author!
 *
 * @param array $data Options for the function.
 * @return string|null Post title for the latest,  * or null if none.
 */
function my_awesome_func( $data ) {
  $posts = get_posts( array(
    'author' => $data['id'],
  ) );

  if ( empty( $posts ) ) {
    return null;
  }

  return $posts[0]->post_title;
}
```

Example 2 (php):
```php
<?php
add_action( 'rest_api_init', function () {
  register_rest_route( 'myplugin/v1', '/author/(?P<id>\d+)', array(
    'methods' => 'GET',
    'callback' => 'my_awesome_func',
  ) );
} );
```

Example 3 (php):
```php
{
  "name": "WordPress Site",
  "description": "Just another WordPress site",
  "url": "http://example.com/",
  "namespaces": [
    "wp/v2",
    "vendor/v1",
    "myplugin/v1",
    "myplugin/v2",
  ]
}
```

Example 4 (php):
```php
<?php
function my_awesome_func( WP_REST_Request $request ) {
  // You can access parameters via direct array access on the object:
  $param = $request['some_param'];

  // Or via the helper method:
  $param = $request->get_param( 'some_param' );

  // You can get the combined, merged set of parameters:
  $parameters = $request->get_params();

  // The individual sets of parameters are also available, if needed:
  $parameters = $request->get_url_params();
  $parameters = $request->get_query_params();
  $parameters = $request->get_body_params();
  $parameters = $request->get_json_params();
  $pa
...
```

---

## Navigations

**URL:** https://developer.wordpress.org/rest-api/reference/wp_navigations

**Contents:**
- Navigations
- In this article
- Schema
- List Navigations
  - Definition
  - Example Request
  - Arguments
- Create a Navigation
  - Arguments
  - Definition

The schema defines all the fields that exist within a navigation record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string or null, Format: datetime (details)

Context: view, edit, embed

JSON data type: string or null, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

One of: publish, future, draft, pending, private

JSON data type: string

Context: view, edit, embed

JSON data type: string

JSON data type: object

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: string

Query this endpoint to retrieve a collection of navigations. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/navigation

$ curl https://example.com/wp-json/wp/v2/navigation

One of: view, embed, edit

One of: author, date, id, include, modified, parent, relevance, slug, include_slugs, title

POST /wp/v2/navigation

GET /wp/v2/navigation/<id>

Query this endpoint to retrieve a specific navigation record.

$ curl https://example.com/wp-json/wp/v2/navigation/<id>

One of: view, embed, edit

POST /wp/v2/navigation/<id>

DELETE /wp/v2/navigation/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/navigation/<id>

Improve it on GitHub: Navigations

See list of changes: Navigations

---

## Widget Types

**URL:** https://developer.wordpress.org/rest-api/reference/widget-types

**Contents:**
- Widget Types
- In this article
- Schema
- Retrieve a Widget Type
  - Definition & Example Request
  - Arguments
- Retrieve a Widget Type
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a widget type record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: view, edit, embed

JSON data type: boolean

Context: view, edit, embed

JSON data type: string

Context: embed, view, edit

GET /wp/v2/widget-types

Query this endpoint to retrieve a specific widget type record.

$ curl https://example.com/wp-json/wp/v2/widget-types

One of: view, embed, edit

GET /wp/v2/widget-types/<id>

Query this endpoint to retrieve a specific widget type record.

$ curl https://example.com/wp-json/wp/v2/widget-types/<id>

One of: view, embed, edit

Improve it on GitHub: Widget Types

See list of changes: Widget Types

---

## Pattern Directory Items

**URL:** https://developer.wordpress.org/rest-api/reference/pattern-directory-items

**Contents:**
- Pattern Directory Items
- In this article
- Schema
- List Pattern Directory Items
  - Definition
  - Example Request
  - Arguments

The schema defines all the fields that exist within a pattern directory item record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: array

Query this endpoint to retrieve a collection of pattern directory items. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/pattern-directory/patterns

$ curl https://example.com/wp-json/wp/v2/pattern-directory/patterns

One of: view, embed, edit

One of: author, date, id, include, modified, parent, relevance, slug, include_slugs, title, favorite_count

Improve it on GitHub: Pattern Directory Items

See list of changes: Pattern Directory Items

---

## Site Settings

**URL:** https://developer.wordpress.org/rest-api/reference/settings

**Contents:**
- Site Settings
- In this article
- Schema
- Retrieve a Site Setting
  - Definition & Example Request
- Update a Site Setting
  - Arguments
  - Definition
  - Example Request

The schema defines all the fields that exist within a Site Setting record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

JSON data type: string

JSON data type: string, Format: uri

JSON data type: string, Format: email

JSON data type: string

JSON data type: string

JSON data type: string

JSON data type: integer

JSON data type: string

JSON data type: boolean

JSON data type: integer

JSON data type: string

JSON data type: integer

JSON data type: string

JSON data type: integer

JSON data type: integer

JSON data type: string

JSON data type: string

JSON data type: integer

JSON data type: integer

Query this endpoint to retrieve a specific Site Setting record.

$ curl https://example.com/wp-json/wp/v2/settings

Improve it on GitHub: Site Settings

See list of changes: Site Settings

---

## Plugins

**URL:** https://developer.wordpress.org/rest-api/reference/plugins

**Contents:**
- Plugins
- In this article
- Schema
- Retrieve a Plugin
  - Definition & Example Request
  - Arguments
- Create a Plugin
  - Arguments
  - Definition
- Retrieve a Plugin

The schema defines all the fields that exist within a plugin record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

One of: inactive, active

JSON data type: string

Context: view, edit, embed

JSON data type: string, Format: uri

JSON data type: object

JSON data type: string, Format: uri

JSON data type: object

JSON data type: string

JSON data type: boolean

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string

Query this endpoint to retrieve a specific plugin record.

$ curl https://example.com/wp-json/wp/v2/plugins

One of: view, embed, edit

One of: inactive, active

GET /wp/v2/plugins/<plugin>?)

Query this endpoint to retrieve a specific plugin record.

$ curl https://example.com/wp-json/wp/v2/plugins/<plugin>?)

One of: view, embed, edit

One of: view, embed, edit

POST /wp/v2/plugins/<plugin>?)

One of: view, embed, edit

DELETE /wp/v2/plugins/<plugin>?)

$ curl -X DELETE https://example.com/wp-json/wp/v2/plugins/<plugin>?)

Improve it on GitHub: Plugins

See list of changes: Plugins

---

## Frequently Asked Questions

**URL:** https://developer.wordpress.org/rest-api/frequently-asked-questions

**Contents:**
- Frequently Asked Questions
- In this article
- Can I disable the REST API?
- Require Authentication for All Requests
- Can I make API requests from PHP within a plugin?
- How do I use the _embed parameter on internal requests?
- What happened to the ?filter= query parameter?
- Query parameters are not working
- Why is Authentication not working?
  - Apache

This page provides solutions to some common questions and problems that may arise while using the API. If your question is not explained here it may have been answered in the WordPress support forums.

You should not disable the REST API; doing so will break WordPress Admin functionality that depends on the API being active. However, you may use a filter to require that API consumers be authenticated, which effectively prevents anonymous external access. See below for more information.

You can require authentication for all REST API requests by adding an is_user_logged_in check to the rest_authentication_errors filter.

Note: The incoming callback parameter can be either null, a WP_Error, or a boolean. The type of the parameter indicates the state of authentication:

Yes, you can! Use rest_do_request to make API requests internally within other WordPress code:

Setting the _embed param on the request object won’t work.

Instead, manually call the WP_REST_Server::response_to_data function.

When the REST API was merged into WordPress core the ?filter query parameter was removed to prevent future compatibility and maintenance issues. The ability to pass arbitrary WP_Query arguments to the API using a ?filter query parameter was necessary at the genesis of the REST API project, but most API response filtering functionality has been superseded by more robust query parameters like ?categories=, ?slug= and ?per_page=.

First-party query parameters should be used whenever possible. However, the rest-filter plugin restores the ability to pass arbitrary ?filter values in API request if needed.

If you find that query parameters such as ?page=2 or ?_embed are not having any effect, your server may not be properly configured to detect them. If you are using Nginx to serve your website, look for a try_files line in your site configuration. If it looks like this:

Adding $is_args (which will print a ? character if query arguments are found) will allow WordPress to properly receive and interpret the query parameters.

If you’re finding that you are sending Authentication headers but the request is not being accepted, and you are using a CGI environment, your webserver may be stripping the headers. Please try adding the appropriate configuration below to remedy this.

Add the following to a configuration file or .htaccess:

Add the following to your server configurations fastcgi section:

Cross-Origin Resource Sharing (CORS) is a mechanism which allows a website to cont

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
add_filter( 'rest_authentication_errors', function( $result ) {
    // If a previous authentication check was applied,
    // pass that result along without modification.
    if ( true === $result || is_wp_error( $result ) ) {
        return $result;
    }

    // No authentication has been performed yet.
    // Return an error if user is not logged in.
    if ( ! is_user_logged_in() ) {
        return new WP_Error(
            'rest_not_logged_in',
            __( 'You are not currently logged in.' ),
            array( 'status' => 401 )
        );
    }

    // Our custom authentication chec
...
```

Example 2 (php):
```php
$request = new WP_REST_Request( 'GET', '/wp/v2/posts' );
// Set one or more request query parameters
$request->set_param( 'per_page', 20 );
$response = rest_do_request( $request );
```

Example 3 (php):
```php
$request = new WP_REST_Request( 'GET', '/wp/v2/posts' );
$request->set_param( '_embed', 1 );
$response = rest_do_request( $request );
```

Example 4 (php):
```php
$request = new WP_REST_Request( 'GET', '/wp/v2/posts' );
$response = rest_do_request( $request );
$data = rest_get_server()->response_to_data( $response, true );
var_dump( $data['_embedded'] );
```

---

## Statuses

**URL:** https://developer.wordpress.org/rest-api/reference/post-statuses

**Contents:**
- Statuses
- In this article
- Schema
- Retrieve a Status
  - Definition & Example Request
  - Arguments
- Retrieve a Status
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a status record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: embed, view, edit

JSON data type: boolean

JSON data type: boolean

JSON data type: boolean

JSON data type: boolean

JSON data type: boolean

JSON data type: string

Context: embed, view, edit

JSON data type: boolean

Query this endpoint to retrieve a specific status record.

$ curl https://example.com/wp-json/wp/v2/statuses

One of: view, embed, edit

GET /wp/v2/statuses/<status>

Query this endpoint to retrieve a specific status record.

$ curl https://example.com/wp-json/wp/v2/statuses/<status>

One of: view, embed, edit

Improve it on GitHub: Statuses

See list of changes: Statuses

---

## Adding REST API Support For Custom Content Types

**URL:** https://developer.wordpress.org/rest-api/extending-the-rest-api/adding-rest-api-support-for-custom-content-types

**Contents:**
- Adding REST API Support For Custom Content Types
- In this article
- Registering A Custom Post Type With REST API Support
- Registering A Custom Taxonomy With REST API Support
- Adding REST API Support To Existing Content Types
- Custom Link Relationships

The REST API can create routes for custom post types and custom taxonomies inside of the wp/v2 namespace, using the same controllers as the default post type or taxonomy term controllers. Alternatively, you can use your own controllers and namespace. This document will cover using the default controllers for your custom content type’s API routes. This is the easiest way and ensures the highest chance of compatibility with third parties.

When registering a custom post type, if you want it to be available via the REST API you should set 'show_in_rest' => true in the arguments passed to register_post_type. Setting this argument to true will add a route in the wp/v2 namespace.

You can optionally set the rest_base argument to change the base url, which will otherwise default to the post type’s name. In the example below, “books” is used as the value of rest_base. This will make the URL for the route wp-json/wp/v2/books instead of wp-json/wp/v2/book/, which would have been the default.

In addition, you can pass an argument for rest_controller_class. This class must be a subclass of WP_REST_Controller. By default, WP_REST_Posts_Controller is used as the controller. If you are using a custom controller, then you likely will not be within the wp/v2 namespace.

Here is an example of registering a post type, with full labels, support for the REST API, a customized rest_base, and explicit registry of the default controller:

If you are using a custom rest_controller_class, then the REST API is unable to automatically determine the route for a given post. In this case, you can use the rest_route_for_post filter to provide this information. This allows for your custom post type to be properly formatted in the Search endpoint and enables automated discovery links.

Registering a custom taxonomy with REST API support is very similar to registering a custom post type: pass 'show_in_rest' => true in the arguments passed to register_taxonomy. You may optionally pass rest_base to change the base url for the taxonomy’s routes.

The default controller for taxonomies is WP_REST_Terms_Controller. You may modify this with the rest_controller_class if you choose to use a custom controller.

Here is an example of how to register a custom taxonomy with REST API support:

If you are using a custom rest_controller_class, then the REST API is unable to automatically determine the route for a given term. In this case, you can use the rest_route_for_term filter to provide this informat

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
/**
 * Register a book post type, with REST API support
 *
 * Based on example at: https://developer.wordpress.org/reference/functions/register_post_type
 */
add_action( 'init', 'my_book_cpt' );
function my_book_cpt() {
    $args = array(
      'public'       => true,
      'show_in_rest' => true,
      'label'        => 'Books'
    );
    register_post_type( 'book', $args );
}
```

Example 2 (php):
```php
/**
 * Register a book post type, with REST API support
 *
 * Based on example at: https://developer.wordpress.org/reference/functions/register_post_type
 */
add_action( 'init', 'my_book_cpt' );
function my_book_cpt() {
  $labels = array(
    'name'               => _x( 'Books', 'post type general name', 'your-plugin-textdomain' ),
    'singular_name'      => _x( 'Book', 'post type singular name', 'your-plugin-textdomain' ),
    'menu_name'          => _x( 'Books', 'admin menu', 'your-plugin-textdomain' ),
    'name_admin_bar'     => _x( 'Book', 'add new on admin bar', 'your-plugin-textdomain'
...
```

Example 3 (php):
```php
function my_plugin_rest_route_for_post( $route, $post ) {
    if ( $post->post_type === 'book' ) {
        $route = '/wp/v2/books/' . $post->ID;
    }

    return $route;
}
add_filter( 'rest_route_for_post', 'my_plugin_rest_route_for_post', 10, 2 );
```

Example 4 (php):
```php
/**
 * Register a genre post type, with REST API support
 *
 * Based on example at: https://developer.wordpress.org/reference/functions/register_taxonomy/
 */
add_action( 'init', 'my_book_taxonomy', 30 );
function my_book_taxonomy() {

  $labels = array(
    'name'              => _x( 'Genres', 'taxonomy general name' ),
    'singular_name'     => _x( 'Genre', 'taxonomy singular name' ),
    'search_items'      => __( 'Search Genres' ),
    'all_items'         => __( 'All Genres' ),
    'parent_item'       => __( 'Parent Genre' ),
    'parent_item_colon' => __( 'Parent Genre:' ),
    'edit_ite
...
```

---

## Linking and Embedding

**URL:** https://developer.wordpress.org/rest-api/using-the-rest-api/linking-and-embedding

**Contents:**
- Linking and Embedding
- In this article
- Links
  - Example Response
- Embedding
  - Example Response

The WP REST API incorporates hyperlinking throughout the API to allow discoverability and browsability, as well as embedding related resources together in one response. While the REST API does not completely conform to the entire HAL standard, it implements the ._links and ._embedded properties from that standard as described below.

The _links property of the response object contains a map of links to other API resources, grouped by “relation.” The relation specifies how the linked resource relates to the primary resource.

Examples include: – author – describing a relationship between a resource and its author – wp:term – describing the relationship between a post and its tags or categories

The relation is either a – standardized relation – a URI relation – like https://api.w.org/term – or a Compact URI relation – like wp:term

Compact URI relations can be normalized to full URI relations to ensure full compatibility if required. This is similar to HTML <link> tags, or <a rel=""> links.

The links are an object containing a href property with an absolute URL to the resource, as well as other optional properties. These include content types, disambiguation information, and data on actions that can be taken with the link.

For collection responses (those that return a list of objects rather than a top-level object), each item contains links, and the top-level response includes links via the Link header instead.

If your client library does not allow accessing headers, you can use the _envelope parameter to include the headers as body data instead.

A typical single post request (/wp/v2/posts/42):

Optionally, some linked resources may be included in the response to reduce the number of HTTP requests required. These resources are “embedded” into the main response.

Embedding is triggered by setting the _embed query parameter on the request. This will then include embedded resources under the _embedded key adjacent to the _links key. The layout of this object mirrors the _links object, but includes the embedded resource in place of the link properties.

Only links with the embeddable flag set to true can be embedded, and _embed will cause all embeddable links to be embedded. Only relations containing embedded responses are included in _embedded, however relations with mixed embeddable and unembeddable links will contain dummy responses for the unembeddable links to ensure numeric indexes match those in _links.

When embedding a collection response, for inst

*[Content truncated]*

**Examples:**

Example 1 (js):
```js
{
  "id": 42,
  "_links": {
    "collection": [
      {
        "href": "https://example.com/wp-json/wp/v2/posts"
      }
    ],
    "author": [
      {
        "href": "https://example.com/wp-json/wp/v2/users/1",
        "embeddable": true
      }
    ]
  }
}
```

Example 2 (js):
```js
{
  "id": 42,
  "_links": {
    "collection": [
      {
        "href": "https://example.com/wp-json/wp/v2/posts"
      }
    ],
    "author": [
      {
        "href": "https://example.com/wp-json/wp/v2/users/1",
        "embeddable": true
      }
    ]
  },
  "_embedded": {
    "author": {
      "id": 1,
      "name": "admin",
      "description": "Site administrator"
    }
  }
}
```

---

## Template Revisions

**URL:** https://developer.wordpress.org/rest-api/reference/wp_template-revisions

**Contents:**
- Template Revisions
- In this article
- Schema
- List Template Revisions
  - Definition
  - Example Request
  - Arguments
- Retrieve a Template Revision
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a template revision record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object or string

Context: embed, view, edit

JSON data type: object or string

Context: embed, view, edit

Query this endpoint to retrieve a collection of template revisions. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/templates/<parent>/revisions

$ curl https://example.com/wp-json/wp/v2/templates/<parent>/revisions

One of: view, embed, edit

One of: date, id, include, relevance, slug, include_slugs, title

GET /wp/v2/templates/<parent>/revisions/<id>

Query this endpoint to retrieve a specific template revision record.

$ curl https://example.com/wp-json/wp/v2/templates/<parent>/revisions/<id>

One of: view, embed, edit

DELETE /wp/v2/templates/<parent>/revisions/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/templates/<parent>/revisions/<id>

GET /wp/v2/templates/<id>/autosaves

Query this endpoint to retrieve a specific template revision record.

$ curl https://example.com/wp-json/wp/v2/templates/<id>/autosaves

One of: view, embed, edit

POST /wp/v2/templates/<id>/autosaves

GET /wp/v2/templates/<parent>/autosaves/<id>

Query this endpoint to retrieve a specific template revision record.

$ curl https://example.com/wp-json/wp/v2/templates/<parent>/autosaves/<id>

One of: view, embed, edit

Improve it on GitHub: Template Revisions

See list of changes: Template Revisions

---

## Using the REST API

**URL:** https://developer.wordpress.org/rest-api/using-the-rest-api

**Contents:**
- Using the REST API
- Resources & Utilities

These articles explore the basic structure of the WordPress REST API.

Global Parameters: learn about the global REST API query parameters that apply to every endpoint

Pagination: work with large collections of resources & control how many records you receive from the REST API

Linking & Embedding: understand how to read and modify connections between different objects, and embed related resources such as author and media data in the REST API’s responses

Discovery: determine what REST API resources a site supports, and where they are located

Authentication: authorize your REST API requests so that you can create, update and delete your data

Frequently Asked Questions: see some of the most frequent inquiries about the REST API and learn how to solve common problems

Backbone.js Client: interact with the API from within WP-Admin using Backbone models & collections

Client Libraries: utilities in a variety of programming languages that simplify interacting with the API

Improve it on GitHub: Using the REST API

See list of changes: Using the REST API

---

## Users

**URL:** https://developer.wordpress.org/rest-api/reference/users

**Contents:**
- Users
- In this article
- Schema
- List Users
  - Definition
  - Example Request
  - Arguments
- Create a User
  - Arguments
  - Definition

The schema defines all the fields that exist within a user record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: embed, view, edit

JSON data type: string

JSON data type: string

Context: embed, view, edit

JSON data type: string

JSON data type: string

JSON data type: string, Format: email

JSON data type: string, Format: uri

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string, Format: uri

Context: embed, view, edit

JSON data type: string

JSON data type: string

JSON data type: string

Context: embed, view, edit

JSON data type: string, Format: datetime (details)

JSON data type: array

JSON data type: string

JSON data type: object

JSON data type: object

JSON data type: object

Context: embed, view, edit

JSON data type: object

Query this endpoint to retrieve a collection of users. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/users

One of: view, embed, edit

One of: id, include, name, registered_date, slug, include_slugs, email, url

GET /wp/v2/users/<id>

Query this endpoint to retrieve a specific user record.

$ curl https://example.com/wp-json/wp/v2/users/<id>

One of: view, embed, edit

POST /wp/v2/users/<id>

DELETE /wp/v2/users/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/users/<id>

Query this endpoint to retrieve a specific user record.

$ curl https://example.com/wp-json/wp/v2/users/me

One of: view, embed, edit

DELETE /wp/v2/users/me

$ curl -X DELETE https://example.com/wp-json/wp/v2/users/me

Improve it on GitHub: Users

See list of changes: Users

---

## Page Revisions

**URL:** https://developer.wordpress.org/rest-api/reference/page-revisions

**Contents:**
- Page Revisions
- In this article
- Schema
- List Page Revisions
  - Definition
  - Example Request
  - Arguments
- Retrieve a Page Revision
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a page revision record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: object

JSON data type: object

Context: view, edit, embed

Query this endpoint to retrieve a collection of page revisions. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/pages/<parent>/revisions

$ curl https://example.com/wp-json/wp/v2/pages/<parent>/revisions

One of: view, embed, edit

One of: date, id, include, relevance, slug, include_slugs, title

GET /wp/v2/pages/<parent>/revisions/<id>

Query this endpoint to retrieve a specific page revision record.

$ curl https://example.com/wp-json/wp/v2/pages/<parent>/revisions/<id>

One of: view, embed, edit

DELETE /wp/v2/pages/<parent>/revisions/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/pages/<parent>/revisions/<id>

GET /wp/v2/pages/<id>/autosaves

Query this endpoint to retrieve a specific page revision record.

$ curl https://example.com/wp-json/wp/v2/pages/<id>/autosaves

One of: view, embed, edit

POST /wp/v2/pages/<id>/autosaves

GET /wp/v2/pages/<parent>/autosaves/<id>

Query this endpoint to retrieve a specific page revision record.

$ curl https://example.com/wp-json/wp/v2/pages/<parent>/autosaves/<id>

One of: view, embed, edit

Improve it on GitHub: Page Revisions

See list of changes: Page Revisions

---

## Template_Parts

**URL:** https://developer.wordpress.org/rest-api/reference/wp_template_parts

**Contents:**
- Template_Parts
- In this article
- Schema
- Retrieve a Template_Part
  - Definition & Example Request
  - Arguments
- Create a Template_Part
  - Arguments
  - Definition
- Retrieve a Template_Part

The schema defines all the fields that exist within a template_part record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: object or string

Context: embed, view, edit

JSON data type: object or string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

One of: publish, future, draft, pending, private

JSON data type: integer

Context: embed, view, edit

Context: embed, view, edit

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string

Context: embed, view, edit

GET /wp/v2/template-parts

Query this endpoint to retrieve a specific template_part record.

$ curl https://example.com/wp-json/wp/v2/template-parts

One of: view, embed, edit

One of: publish, future, draft, pending, private

POST /wp/v2/template-parts

GET /wp/v2/template-parts/<id>?)[\/\w%-]+)

Query this endpoint to retrieve a specific template_part record.

$ curl https://example.com/wp-json/wp/v2/template-parts/<id>?)[\/\w%-]+)

One of: view, embed, edit

POST /wp/v2/template-parts/<id>?)[\/\w%-]+)

DELETE /wp/v2/template-parts/<id>?)[\/\w%-]+)

$ curl -X DELETE https://example.com/wp-json/wp/v2/template-parts/<id>?)[\/\w%-]+)

Improve it on GitHub: Template_Parts

See list of changes: Template_Parts

---

## Schema

**URL:** https://developer.wordpress.org/rest-api/extending-the-rest-api/schema

**Contents:**
- Schema
- In this article
- Overview
  - JSON
  - Resource Schema
  - Argument Schema
  - Summary
- JSON Schema Basics
  - API
  - Caching Schema

A schema is metadata that tells us how our data is structured. Most databases implement some form of schema which enables us to reason about our data in a more structured manner. The WordPress REST API utilizes JSON Schema to handle the structuring of its data. You can implement endpoints without using a schema, but you will be missing out on a lot of things. It is up to you to decide what suits you best.

First, let’s talk about JSON a bit. JSON is a human readable data format that resembles JavaScript objects. JSON stands for JavaScript Object Notation. JSON is growing wildly in popularity and seems to be taking the world of data structure by storm. The WordPress REST API uses a special specification for JSON known as JSON schema. To learn more about JSON Schema please check out the JSON Schema website and this easier to understand introduction to JSON Schema. Schema affords us many benefits: improved testing, discoverability, and overall better structure. Let’s look at a JSON blob of data.

A JSON parser will go through that data no problem and won’t complain about anything, because it is valid JSON. The clients and servers know nothing about the data and what to expect they just see the JSON. By implementing schema we can actually simplify our codebase. Schema will help structure our data better so our applications can more easily reason about our interactions with the WordPress REST API. The WordPress REST API does not force you to use schema, but it is encouraged. There are two ways in which schema data is incorporated into the API; schema for resources and schema for our registered arguments.

The schema for a resource indicates what fields are present for a particular object. When we register our routes we can also specify the resource schema for the route. Let’s look at what a simple comment schema might look like in a PHP representation of JSON schema.

If you notice, each comment resource now matches up to our schema that we specified. We made this switch in prefix_rest_prepare_comment(). By creating schema for our resources, we can now view this schema by making OPTIONS requests. Why is this useful? If we wanted other languages, JavaScript for example, to interpret our data and validate the data from our endpoint, JavaScript would need to know how our data is structured. When we provide schema, we open the doors for other authors, and ourselves, to build on top of our endpoints in a consistent manner.

Schema provides machine readable data, so 

*[Content truncated]*

**Examples:**

Example 1 (js):
```js
{
    "shouldBeArray": 'LOL definitely not an array',
    "shouldBeInteger": ['lolz', 'you', 'need', 'schema'],
    "shouldBeString": 123456789
}
```

Example 2 (php):
```php
// Register our routes.
function prefix_register_my_comment_route() {
    register_rest_route( 'my-namespace/v1', '/comments', array(
        // Notice how we are registering multiple endpoints the 'schema' equates to an OPTIONS request.
        array(
            'methods'  => 'GET',
            'callback' => 'prefix_get_comment_sample',
        ),
        // Register our schema callback.
        'schema' => 'prefix_get_comment_schema',
    ) );
}

add_action( 'rest_api_init', 'prefix_register_my_comment_route' );

/**
 * Grabs the five most recent comments and outputs them as a rest response
...
```

Example 3 (php):
```php
// Register our routes.
function prefix_register_my_arg_route() {
    register_rest_route( 'my-namespace/v1', '/schema-arg', array(
        // Here we register our endpoint.
        array(
            'methods'  => 'GET',
            'callback' => 'prefix_get_item',
            'args' => prefix_get_endpoint_args(),
        ),
    ) );
}

// Hook registration into 'rest_api_init' hook.
add_action( 'rest_api_init', 'prefix_register_my_arg_route' );

/**
 * Returns the request argument `my-arg` as a rest response.
 *
 * @param WP_REST_Request $request Current request.
 */
function prefix_get_item
...
```

Example 4 (php):
```php
/**
     * Retrieves the attachment's schema, conforming to JSON Schema.
     *
     * @return array Item schema as an array.
     */
    public function get_item_schema() {
        // Returned cached copy whenever available.
        if ( $this->schema ) {
            return $this->add_additional_fields_schema( $this->schema );
        }

        $schema = parent::get_item_schema();
        // Add endpoint-specific properties to Schema.
        $schema['properties']['field_name'] = array( /* ... */ );
        $schema['properties']['etcetera'] = array( /* ... */ );

        // Cache generated s
...
```

---

## Pages

**URL:** https://developer.wordpress.org/rest-api/reference/pages

**Contents:**
- Pages
- In this article
- Schema
- List Pages
  - Definition
  - Example Request
  - Arguments
- Create a Page
  - Arguments
  - Definition

The schema defines all the fields that exist within a page record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string or null, Format: datetime (details)

Context: view, edit, embed

JSON data type: string or null, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: string

Context: view, edit, embed

JSON data type: string

One of: publish, future, draft, pending, private

JSON data type: string

Context: view, edit, embed

JSON data type: string

JSON data type: string

JSON data type: string

JSON data type: integer

JSON data type: object

Context: view, edit, embed

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: string

JSON data type: string

JSON data type: integer

JSON data type: object

JSON data type: string

Query this endpoint to retrieve a collection of pages. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/pages

One of: view, embed, edit

One of: author, date, id, include, modified, parent, relevance, slug, include_slugs, title, menu_order

GET /wp/v2/pages/<id>

Query this endpoint to retrieve a specific page record.

$ curl https://example.com/wp-json/wp/v2/pages/<id>

One of: view, embed, edit

POST /wp/v2/pages/<id>

DELETE /wp/v2/pages/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/pages/<id>

Improve it on GitHub: Pages

See list of changes: Pages

---

## Types

**URL:** https://developer.wordpress.org/rest-api/reference/post-types

**Contents:**
- Types
- In this article
- Schema
- Retrieve a Type
  - Definition & Example Request
  - Arguments
- Retrieve a Type
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a type record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: object

JSON data type: string

JSON data type: boolean

JSON data type: boolean

JSON data type: object

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object

JSON data type: string or boolean

JSON data type: array

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object

JSON data type: string or null

Context: view, edit, embed

Query this endpoint to retrieve a specific type record.

$ curl https://example.com/wp-json/wp/v2/types

One of: view, embed, edit

GET /wp/v2/types/<type>

Query this endpoint to retrieve a specific type record.

$ curl https://example.com/wp-json/wp/v2/types/<type>

One of: view, embed, edit

Improve it on GitHub: Types

See list of changes: Types

---

## Media

**URL:** https://developer.wordpress.org/rest-api/reference/media

**Contents:**
- Media
- In this article
- Schema
- List Media
  - Definition
  - Example Request
  - Arguments
- Create a Media Item
  - Arguments
  - Definition

The schema defines all the fields that exist within a Media Item record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string or null, Format: datetime (details)

Context: view, edit, embed

JSON data type: string or null, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: string

Context: view, edit, embed

JSON data type: string

One of: publish, future, draft, pending, private

JSON data type: string

Context: view, edit, embed

JSON data type: string

JSON data type: string

JSON data type: object

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: string

JSON data type: string

JSON data type: object

JSON data type: string

JSON data type: string

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: object

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: integer

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: array

Query this endpoint to retrieve a collection of media. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/media

One of: view, embed, edit

One of: author, date, id, include, modified, parent, relevance, slug, include_slugs, title

GET /wp/v2/media/<id>

Query this endpoint to retrieve a specific Media Item record.

$ curl https://example.com/wp-json/wp/v2/media/<id>

One of: view, embed, edit

POST /wp/v2/media/<id>

DELETE /wp/v2/media/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/media/<id>

Improve it on GitHub: Media

See list of changes: Media

---

## Taxonomies

**URL:** https://developer.wordpress.org/rest-api/reference/taxonomies

**Contents:**
- Taxonomies
- In this article
- Schema
- Retrieve a Taxonomy
  - Definition & Example Request
  - Arguments
- Retrieve a Taxonomy
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a taxonomy record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: object

JSON data type: string

JSON data type: boolean

JSON data type: object

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: boolean

JSON data type: array

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object

GET /wp/v2/taxonomies

Query this endpoint to retrieve a specific taxonomy record.

$ curl https://example.com/wp-json/wp/v2/taxonomies

One of: view, embed, edit

GET /wp/v2/taxonomies/<taxonomy>

Query this endpoint to retrieve a specific taxonomy record.

$ curl https://example.com/wp-json/wp/v2/taxonomies/<taxonomy>

One of: view, embed, edit

Improve it on GitHub: Taxonomies

See list of changes: Taxonomies

---

## Templates

**URL:** https://developer.wordpress.org/rest-api/reference/wp_templates

**Contents:**
- Templates
- In this article
- Schema
- Retrieve a Template
  - Definition & Example Request
  - Arguments
- Create a Template
  - Arguments
  - Definition
- Retrieve a Template

The schema defines all the fields that exist within a template record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: object or string

Context: embed, view, edit

JSON data type: object or string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

One of: publish, future, draft, pending, private

JSON data type: integer

Context: embed, view, edit

Context: embed, view, edit

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: embed, view, edit

Query this endpoint to retrieve a specific template record.

$ curl https://example.com/wp-json/wp/v2/templates

One of: view, embed, edit

One of: publish, future, draft, pending, private

POST /wp/v2/templates

GET /wp/v2/templates/<id>?)[\/\w%-]+)

Query this endpoint to retrieve a specific template record.

$ curl https://example.com/wp-json/wp/v2/templates/<id>?)[\/\w%-]+)

One of: view, embed, edit

POST /wp/v2/templates/<id>?)[\/\w%-]+)

DELETE /wp/v2/templates/<id>?)[\/\w%-]+)

$ curl -X DELETE https://example.com/wp-json/wp/v2/templates/<id>?)[\/\w%-]+)

Improve it on GitHub: Templates

See list of changes: Templates

---

## Post Revisions

**URL:** https://developer.wordpress.org/rest-api/reference/post-revisions

**Contents:**
- Post Revisions
- In this article
- Schema
- List Post Revisions
  - Definition
  - Example Request
  - Arguments
- Retrieve a Post Revision
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a post revision record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: object

JSON data type: object

Context: view, edit, embed

Query this endpoint to retrieve a collection of post revisions. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/posts/<parent>/revisions

$ curl https://example.com/wp-json/wp/v2/posts/<parent>/revisions

One of: view, embed, edit

One of: date, id, include, relevance, slug, include_slugs, title

GET /wp/v2/posts/<parent>/revisions/<id>

Query this endpoint to retrieve a specific post revision record.

$ curl https://example.com/wp-json/wp/v2/posts/<parent>/revisions/<id>

One of: view, embed, edit

DELETE /wp/v2/posts/<parent>/revisions/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/posts/<parent>/revisions/<id>

GET /wp/v2/posts/<id>/autosaves

Query this endpoint to retrieve a specific post revision record.

$ curl https://example.com/wp-json/wp/v2/posts/<id>/autosaves

One of: view, embed, edit

POST /wp/v2/posts/<id>/autosaves

GET /wp/v2/posts/<parent>/autosaves/<id>

Query this endpoint to retrieve a specific post revision record.

$ curl https://example.com/wp-json/wp/v2/posts/<parent>/autosaves/<id>

One of: view, embed, edit

Improve it on GitHub: Post Revisions

See list of changes: Post Revisions

---

## Glossary

**URL:** https://developer.wordpress.org/rest-api/glossary

**Contents:**
- Glossary
- In this article
- Controller
- HEAD, GET, POST, PUT, and DELETE Requests
- HTTP Client
- Resource
- Routes / Endpoints
- Schema

New to REST APIs? Get up to speed with phrases used throughout our documentation.

Model-View-Controller is a standard pattern in software development. If you aren’t already familiar with it, you should do a bit of reading to get up to speed.

Within WP-API, we’ve adopted the controller concept to have a standard pattern for the classes representing our resource endpoints. All resource endpoints extend WP_REST_Controller to ensure they implement common methods.

These “HTTP verbs” represent the type of action a HTTP client might perform against a resource. For instance, GET requests are used to fetch a Post’s data, whereas DELETE requests are used to delete a Post. They’re collectively called “HTTP verbs” because they’re standardized across the web.

If you’re familiar with WordPress functions, a GET request is the equivalent of wp_remote_get(), and a POST request is the same as wp_remote_post().

The phrase “HTTP Client” refers to the tool you use to interact with WP-API. You might use Postman (Chrome) or REST Easy (Firefox) to test requests in your browser, or httpie to test requests at the commandline.

WordPress itself provides a HTTP Client in the WP_HTTP class and related functions (e.g. wp_remote_get()). This can be used to access one WordPress site from another.

A “Resource” is a discrete entity within WordPress. You may know these resources already as Posts, Pages, Comments, Users, Terms, and so on. WP-API permits HTTP clients to perform CRUD operations against resources (CRUD stands for Create, Read, Update, and Delete).

Pragmatically, here’s how you’d typically interact with WP-API resources:

Endpoints are functions available through the API. This can be things like retrieving the API index, updating a post, or deleting a comment. Endpoints perform a specific function, taking some number of parameters and return data to the client.

A route is the “name” you use to access endpoints, used in the URL. A route can have multiple endpoints associated with it, and which is used depends on the HTTP verb.

For example, with the URL `http://example.com/wp-json/wp/v2/posts/123`:

Note: On sites without pretty permalinks, the route is instead added to the URL as the rest_route parameter. For the above example, the full URL would then be `http://example.com/?rest_route=wp/v2/posts/123`

A “schema” is a representation of the format for WP-API’s response data. For instance, the Post schema communicates that a request to get a Post will return id, title, co

*[Content truncated]*

---

## Nav_Menu_Items

**URL:** https://developer.wordpress.org/rest-api/reference/nav_menu_items

**Contents:**
- Nav_Menu_Items
- In this article
- Schema
- List Nav_Menu_Items
  - Definition
  - Example Request
  - Arguments
- Create a Nav_Menu_Item
  - Arguments
  - Definition

The schema defines all the fields that exist within a nav_menu_item record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string or object

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

One of: taxonomy, post_type, post_type_archive, custom

JSON data type: string

Context: view, edit, embed

One of: publish, future, draft, pending, private

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: boolean

Context: view, edit, embed

JSON data type: integer

JSON data type: object

Query this endpoint to retrieve a collection of nav_menu_items. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/menu-items

$ curl https://example.com/wp-json/wp/v2/menu-items

One of: view, embed, edit

One of: author, date, id, include, modified, parent, relevance, slug, include_slugs, title, menu_order

One of: taxonomy, post_type, post_type_archive, custom

One of: publish, future, draft, pending, private

POST /wp/v2/menu-items

GET /wp/v2/menu-items/<id>

Query this endpoint to retrieve a specific nav_menu_item record.

$ curl https://example.com/wp-json/wp/v2/menu-items/<id>

One of: view, embed, edit

POST /wp/v2/menu-items/<id>

DELETE /wp/v2/menu-items/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/menu-items/<id>

Improve it on GitHub: Nav_Menu_Items

See list of changes: Nav_Menu_Items

---

## REST API Handbook

**URL:** https://developer.wordpress.org/rest-api

**Contents:**
- REST API Handbook
- In this article
- What Is A REST API?
- Using the WordPress REST API
- Next Steps

The WordPress REST API provides an interface for applications to interact with your WordPress site by sending and receiving data as JSON (JavaScript Object Notation) objects. It is the foundation of the WordPress Block Editor, and can likewise enable your theme, plugin or custom application to present new, powerful interfaces for managing and publishing your site content.

Using the WordPress REST API you can create a plugin to provide an entirely new admin experience for WordPress, build a brand new interactive front-end experience, or bring your WordPress content into completely separate applications.

The REST API is a developer-oriented feature of WordPress. It provides data access to the content of your site, and implements the same authentication restrictions — content that is public on your site is generally publicly accessible via the REST API, while private content, password-protected content, internal users, custom post types, and metadata is only available with authentication or if you specifically set it to be so. If you are not a developer, the most important thing to understand about the API is that it enables the block editor and modern plugin interfaces without compromising the security or privacy of your site.

An API is an Application Programming Interface. REST, standing for “REpresentational State Transfer,” is a set of concepts for modeling and accessing your application’s data as interrelated objects and collections. The WordPress REST API provides REST endpoints (URLs) representing the posts, pages, taxonomies, and other built-in WordPress data types. Your application can send and receive JSON data to these endpoints to query, modify and create content on your site. JSON is an open standard data format that is lightweight and human-readable, and looks like Objects do in JavaScript. When you request content from or send content to the API, the response will also be returned in JSON. Because JSON is widely supported in many programming languages, developers can build WordPress applications in client-side JavaScript (like the block editor), as mobile apps, or as desktop or command line tools.

The REST API is just one of many APIs provided by WordPress. You can find the documentation on these additional APIs here.

WordPress already provides a rich set of tools and interfaces for building sites, and you should not feel pressured to use the REST API if your site is already working the way you expect. You do not need to use the REST API t

*[Content truncated]*

---

## Client Libraries

**URL:** https://developer.wordpress.org/rest-api/using-the-rest-api/client-libraries

**Contents:**
- Client Libraries
- In this article
- PHP
- JavaScript
- Ruby
- C# / .NET
- Dart / Flutter

The API can be used from any application by sending basic HTTP requests; however, client libraries simplify the process of querying or creating specific resources. These libraries make it easy to connect an external application to the WordPress REST API using a variety of programming languages.

Aside from the Backbone.js client, these libraries are not part of WordPress core, and are not necessarily maintained or endorsed by the WordPress REST API team.

Requests for PHP is a general purpose HTTP request library. While not specifically designed for the WordPress REST API, it is a great tool for interacting with any HTTP API.

WordPress-PHP-SDK is a PHP SDK for the WordPress REST API, which can be installed using composer.

WordPress-SDK is a Laravel package for the WordPress REST API, which can be installed using composer.

The Backbone.js client is built in to WordPress core and provides Backbone.js models & collections for working with REST API resources.

node-wpapi is an isomorphic JavaScript client library for querying or writing to the REST API using an intuitive chaining syntax. It can be used with Node.js or with client-side JavaScript applications.

ember-wordpress provides a connection between Ember Data and the REST API

wp-api-client: a read-only REST API client written in Ruby.

WordPressPCL: a full REST API client written in C#.

wordpress_client: A library exposing a fluent api to interact with the WordPress REST API.

Improve it on GitHub: Client Libraries

See list of changes: Client Libraries

---

## Sidebars

**URL:** https://developer.wordpress.org/rest-api/reference/sidebars

**Contents:**
- Sidebars
- In this article
- Schema
- Retrieve a Sidebar
  - Definition & Example Request
  - Arguments
- Retrieve a Sidebar
  - Definition & Example Request
  - Arguments
- Update a Sidebar

The schema defines all the fields that exist within a sidebar record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

One of: active, inactive

JSON data type: array

Context: embed, view, edit

Query this endpoint to retrieve a specific sidebar record.

$ curl https://example.com/wp-json/wp/v2/sidebars

One of: view, embed, edit

GET /wp/v2/sidebars/<id>

Query this endpoint to retrieve a specific sidebar record.

$ curl https://example.com/wp-json/wp/v2/sidebars/<id>

One of: view, embed, edit

POST /wp/v2/sidebars/<id>

Improve it on GitHub: Sidebars

See list of changes: Sidebars

---

## Reference

**URL:** https://developer.wordpress.org/rest-api/reference

**Contents:**
- Reference
- In this article
- REST API Developer Endpoint Reference
- A Distributed API

The WordPress REST API is organized around REST, and is designed to have predictable, resource-oriented URLs and to use HTTP response codes to indicate API errors. The API uses built-in HTTP features, like HTTP authentication and HTTP verbs, which can be understood by off-the-shelf HTTP clients, and supports cross-origin resource sharing to allow you to interact securely with the API from a client-side web application.

The REST API uses JSON exclusively as the request and response format, including error responses. While the REST API does not completely conform to the HAL standard, it does implement HAL’s ._links and ._embedded properties for linking API resources, and is fully discoverable via hyperlinks in the responses.

The REST API provides public data accessible to any client anonymously, as well as private data only available after authentication. Once authenticated the REST API supports most content management actions, allowing you to build alternative dashboards for a site, enhance your plugins with more responsive management tools, or build complex single-page applications.

This API reference provides information on the specific endpoints available through the API, their parameters, and their response data format.

Unlike many other REST APIs, the WordPress REST API is distributed and available individually on each site that supports it. This means there is no singular API root or base to contact; instead, we have a discovery process that allows interacting with sites without prior contact. The API also exposes self-documentation at the index endpoint, or via an OPTIONS request to any endpoint, allowing human- or machine-discovery of endpoint capabilities.

Improve it on GitHub: Reference

See list of changes: Reference

---

## Themes

**URL:** https://developer.wordpress.org/rest-api/reference/themes

**Contents:**
- Themes
- In this article
- Schema
- Retrieve a Theme
  - Definition & Example Request
  - Arguments
- Retrieve a Theme
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a theme record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

JSON data type: string

JSON data type: object

JSON data type: object

JSON data type: object

JSON data type: boolean

JSON data type: object

JSON data type: string

JSON data type: string

JSON data type: string, Format: uri

JSON data type: object

JSON data type: string

JSON data type: object

JSON data type: object

JSON data type: string

JSON data type: string

One of: inactive, active

Query this endpoint to retrieve a specific theme record.

$ curl https://example.com/wp-json/wp/v2/themes

GET /wp/v2/themes/<stylesheet>?)

Query this endpoint to retrieve a specific theme record.

$ curl https://example.com/wp-json/wp/v2/themes/<stylesheet>?)

Improve it on GitHub: Themes

See list of changes: Themes

---

## Controller Classes

**URL:** https://developer.wordpress.org/rest-api/extending-the-rest-api/controller-classes

**Contents:**
- Controller Classes
- In this article
- Overview
- Controllers
- Benefits of Classes
- Class Inheritance & WP_REST_Controller
- Internal WordPress REST API Classes

To register a new REST route, you must specify a number of callback functions to control endpoint behavior such as how a request is fulfilled, how permissions checks are applied, and how the schema for your resource gets generated. While it is possible to declare all of these methods in an ordinary PHP file without any wrapping namespace or class, all functions declared in that manner coexist in the same global scope. If you decide to use a common function name for your endpoint logic like get_items() and another plugin (or another endpoint in your own plugin) also registers a function with that same name, PHP will fail with a fatal error because the function get_items() is being declared twice.

You can avoid this issue by naming your callback functions using a unique prefix such as myplugin_myendpoint_ to avoid any potential conflics:

You may already be familiar with this approach because it is commonly used within theme functions.php files. However these prefixes are unnecessarily verbose, and several better options exist to group and encapsulate your endpoint’s logic in a more maintainable way.

WordPress currently requires PHP 5.6 or greater. PHP 5.6 supports namespaces, which provide an easy way to encapsulate your endpoint’s functionality. By declaring a namespace at the top of your endpoint’s PHP file, all methods within that namespace will be declared within that namespace and will no longer conflict with global functions. You may then use shorter, more-readable names for your endpoint callbacks.

While these shorter function names are simpler to work with, they don’t provide any other benefits over declaring global functions. For this reason the core REST API endpoints within WordPress are all implemented using a controller class.

The remainder of this page details how to write your own controller class and explains the advantages of doing so.

A controller receives input (a WP_REST_Request object, in the case of the WordPress REST API) and generates response output as WP_REST_Response objects. Let’s look at an example controller class:

This class contains all the same components you may have written using simple functions. The structure of a class gives us a convenient way to refer to related methods using the $this->method_name() syntax, but unlike a namespace the class also permits us to cache values and share logic.

In the get_item_schema method, note that we store the generated schema on the class as $this->schema. Class properties make 

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
function myplugin_myendpoint_register_routes() { /* ... */ }
function myplugin_myendpoint_get_item() { /* ... */ }
function myplugin_myendpoint_get_item_schema() { /* ... */ }
// etcetera

add_action( 'rest_api_init', 'myplugin_myendpoint_register_routes' );
```

Example 2 (php):
```php
namespace MyPlugin\API\MyEndpoint;

function register_routes() { /* ... */ }
function get_item() { /* ... */ }
function get_item_schema() { /* ... */ }
// and so on

add_action( 'rest_api_init', __NAMESPACE__ . '\\register_routes' );
```

Example 3 (php):
```php
class My_REST_Posts_Controller {

    // Here initialize our namespace and resource name.
    public function __construct() {
        $this->namespace     = '/my-namespace/v1';
        $this->resource_name = 'posts';
    }

    // Register our routes.
    public function register_routes() {
        register_rest_route( $this->namespace, '/' . $this->resource_name, array(
            // Here we register the readable endpoint for collections.
            array(
                'methods'   => 'GET',
                'callback'  => array( $this, 'get_items' ),
                'permission_callback' 
...
```

---

## Comments

**URL:** https://developer.wordpress.org/rest-api/reference/comments

**Contents:**
- Comments
- In this article
- Schema
- List Comments
  - Definition
  - Example Request
  - Arguments
- Create a Comment
  - Arguments
  - Definition

The schema defines all the fields that exist within a comment record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: email

JSON data type: string, Format: ip

JSON data type: string

Context: view, edit, embed

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: string

JSON data type: object

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: integer

Context: view, edit, embed

JSON data type: integer

JSON data type: string

JSON data type: string

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: object

Query this endpoint to retrieve a collection of comments. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/comments

One of: view, embed, edit

One of: date, date_gmt, id, include, post, parent, type

GET /wp/v2/comments/<id>

Query this endpoint to retrieve a specific comment record.

$ curl https://example.com/wp-json/wp/v2/comments/<id>

One of: view, embed, edit

POST /wp/v2/comments/<id>

DELETE /wp/v2/comments/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/comments/<id>

Improve it on GitHub: Comments

See list of changes: Comments

---

## Navigation Revisions

**URL:** https://developer.wordpress.org/rest-api/reference/wp_navigation-revisions

**Contents:**
- Navigation Revisions
- In this article
- Schema
- List Navigation Revisions
  - Definition
  - Example Request
  - Arguments
- Retrieve a Navigation Revision
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a navigation revision record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

Query this endpoint to retrieve a collection of navigation revisions. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/navigation/<parent>/revisions

$ curl https://example.com/wp-json/wp/v2/navigation/<parent>/revisions

One of: view, embed, edit

One of: date, id, include, relevance, slug, include_slugs, title

GET /wp/v2/navigation/<parent>/revisions/<id>

Query this endpoint to retrieve a specific navigation revision record.

$ curl https://example.com/wp-json/wp/v2/navigation/<parent>/revisions/<id>

One of: view, embed, edit

DELETE /wp/v2/navigation/<parent>/revisions/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/navigation/<parent>/revisions/<id>

GET /wp/v2/navigation/<id>/autosaves

Query this endpoint to retrieve a specific navigation revision record.

$ curl https://example.com/wp-json/wp/v2/navigation/<id>/autosaves

One of: view, embed, edit

POST /wp/v2/navigation/<id>/autosaves

GET /wp/v2/navigation/<parent>/autosaves/<id>

Query this endpoint to retrieve a specific navigation revision record.

$ curl https://example.com/wp-json/wp/v2/navigation/<parent>/autosaves/<id>

One of: view, embed, edit

Improve it on GitHub: Navigation Revisions

See list of changes: Navigation Revisions

---

## Nav_Menu_Item Revisions

**URL:** https://developer.wordpress.org/rest-api/reference/nav_menu_item-revisions

**Contents:**
- Nav_Menu_Item Revisions
- In this article
- Schema
- Retrieve a Nav_Menu_Item Revision
  - Definition & Example Request
  - Arguments
- Create a Nav_Menu_Item Revision
  - Arguments
  - Definition
- Retrieve a Nav_Menu_Item Revision

The schema defines all the fields that exist within a nav_menu_item revision record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string or object

Context: view, edit, embed

JSON data type: string, Format: uri

GET /wp/v2/menu-items/<id>/autosaves

Query this endpoint to retrieve a specific nav_menu_item revision record.

$ curl https://example.com/wp-json/wp/v2/menu-items/<id>/autosaves

One of: view, embed, edit

POST /wp/v2/menu-items/<id>/autosaves

GET /wp/v2/menu-items/<parent>/autosaves/<id>

Query this endpoint to retrieve a specific nav_menu_item revision record.

$ curl https://example.com/wp-json/wp/v2/menu-items/<parent>/autosaves/<id>

One of: view, embed, edit

Improve it on GitHub: Nav_Menu_Item Revisions

See list of changes: Nav_Menu_Item Revisions

---

## Rendered Blocks

**URL:** https://developer.wordpress.org/rest-api/reference/rendered-blocks

**Contents:**
- Rendered Blocks
- In this article
- Schema
- Create a Rendered Block
  - Arguments
  - Definition

The schema defines all the fields that exist within a Rendered Block record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

POST /wp/v2/block-renderer/<name>

Improve it on GitHub: Rendered Blocks

See list of changes: Rendered Blocks

---

## Extending the REST API

**URL:** https://developer.wordpress.org/rest-api/extending-the-rest-api

**Contents:**
- Extending the REST API
- In this article
- Guides
- Resources

Modifying responses: add fields to REST API response objects using register_meta or register_rest_field

Adding Endpoints: create custom REST API endpoints for your plugin or application

Working with Custom Content Types: learn how to interact with your custom post types and custom taxonomies through the REST API

Defining your API Schema: define the schema for your REST API resources and their arguments

Glossary: get up to speed with phrases used throughout our documentation

Routes & Endpoints: dive deeper into the nuances of REST API routes and the endpoints they provide

Controller Classes: discover how to structure and extend REST API endpoint controller classes

Frequently Asked Questions: see some of the most frequent inquiries about the REST API and learn how to solve common problems

Improve it on GitHub: Extending the REST API

See list of changes: Extending the REST API

---

## Key Concepts

**URL:** https://developer.wordpress.org/rest-api/key-concepts

**Contents:**
- Key Concepts
- In this article
- Routes & Endpoints
- Requests
- Responses
- Schema
- Controller Classes

In this page we’ll break down some of the key concepts and terms associated with the REST API: Routes & Endpoints, Requests, Responses, Schema, and Controller Classes. Each of these concepts play a crucial role in understanding, using, and extending the WordPress REST API, and each is explored in greater depth within this handbook.

In the context of the WordPress REST API a route is a URI which can be mapped to different HTTP methods. The mapping of an individual HTTP method to a route is known as an endpoint.

As an example, if we make a GET request to the URI http://oursite.com/wp-json/ we are returned a JSON response showing what routes are available, and what endpoints are available within each route.

/wp-json/ is a route, and when that route receives a GET request then that request is handled by the endpoint which displays what is known as the index for the WordPress REST API.

The route wp-json/wp/v2/posts by contrast has a GET endpoint which returns a list of posts, but also a POST endpoint which accepts authenticated requests to create new posts.

We will learn how to register our own routes and endpoints in the following sections.

If you are using non-pretty permalinks, you should pass the REST API route as a query string parameter. The route http://oursite.com/wp-json/ in the example above would hence be http://oursite.com/?rest_route=/.

If you get a 404 error when trying to access http://oursite.com/wp-json/, consider enabling pretty permalinks or try using the rest_route parameter instead.

A REST API request is represented within WordPress by an instance of the WP_REST_Request class, which is used to store and retrieve information for the current request. A WP_REST_Request object is automatically generated when you make an HTTP request to a registered API route.

The data specified in this object (derived from the route URI or the JSON payload sent as a part of the request) determines what response you will get back out of the API.

Requests are usually submitted remotely via HTTP but may also be made internally from PHP within WordPress plugin or theme code. There are a lot of neat things you can do using this class, detailed further elsewhere in the handbook.

Responses are the data you get back from the API. The WP_REST_Response class provides a way to interact with the response data returned by endpoints. Responses return the requested data, or can also be used to return errors if something goes wrong while fulfilling the request.

Eac

*[Content truncated]*

---

## Editor Blocks

**URL:** https://developer.wordpress.org/rest-api/reference/blocks

**Contents:**
- Editor Blocks
- In this article
- Schema
- List Editor Blocks
  - Definition
  - Example Request
  - Arguments
- Create a Editor Block
  - Arguments
  - Definition

The schema defines all the fields that exist within a Editor Block record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string or null, Format: datetime (details)

Context: view, edit, embed

JSON data type: string or null, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: uri

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: string

Context: view, edit, embed

JSON data type: string

One of: publish, future, draft, pending, private

JSON data type: string

Context: view, edit, embed

JSON data type: string

JSON data type: object

Context: view, edit, embed

JSON data type: object

JSON data type: object

JSON data type: string

Query this endpoint to retrieve a collection of Editor Blocks. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/blocks

One of: view, embed, edit

One of: author, date, id, include, modified, parent, relevance, slug, include_slugs, title

GET /wp/v2/blocks/<id>

Query this endpoint to retrieve a specific Editor Block record.

$ curl https://example.com/wp-json/wp/v2/blocks/<id>

One of: view, embed, edit

POST /wp/v2/blocks/<id>

DELETE /wp/v2/blocks/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/blocks/<id>

Improve it on GitHub: Editor Blocks

See list of changes: Editor Blocks

---

## Backbone JavaScript Client

**URL:** https://developer.wordpress.org/rest-api/using-the-rest-api/backbone-javascript-client

**Contents:**
- Backbone JavaScript Client
- In this article
- Using
  - Default values
  - Available methods
  - Accepted options
  - Localizing the API Schema
  - Waiting for the client to load
  - Model examples:
  - Collection examples:

The REST API includes a JavaScript/Backbone client library.

The library provides an interface for the WP REST API by providing Backbone Models and Collections for all endpoints exposed through the API Schema.

Activate the WP-API plugin. Enqueue the script directly:

or as a dependency for your script:

The library parses the root endpoint (the ‘Schema’) and creates matching Backbone models and collections. You will now have two root objects available to you: wp.api.models and wp.api.collections.

The models and collections include:

Models: * Category * Comment * Media * Page * PageMeta * PageRevision * Post * PostMeta * PostRevision * Schema * Status * Tag * Taxonomy * Type * User

Collections: * Categories * Comments * Media * PageMeta * PageRevisions * Pages * Posts * Statuses * Tags * Taxonomies * Types * Users

You can use these endpoints as-is to read, update, create and delete items using standard Backbone methods (fetch, sync, save & destroy for models, sync for collections). You can also extend these objects to make them your own, and build your views on top of them.

Each model and collection includes a reference to its default values, for example:

wp.api.models.Post.prototype.args

Each model and collection contains a list of methods the corresponding endpoint supports. For example, models created from wp.api.models.Post have a methods array of:

Each model and collection contains a list of options the corresponding endpoint accepts (note that options are passed as the second parameter when creating models or collections), for example:

wp.api.collections.Posts.prototype.options

The client will accept and use a localized schema as part of the wpApiSettings object. The Schema is currently not passed by default; instead the client makes an ajax request to the API to load the Schema, then caches it in the browser’s session storage (if available). Activating the client-js plugin with SCRIPT_DEBUG enabled uses a localized Schema. Check the client-js example or this branch which attempts to only localize the schema once per client.

Client startup is asynchronous. If the api schema is localized, the client can start immediately; if not the client makes an ajax request to load the schema. The client exposes a load promise for provide a reliable wait to wait for client to be ready:

To create a post and edit its categories, make sure you are logged in, then:

To get the last 10 posts:

To get the last 25 posts:

Use filter to change the order & orde

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
wp_enqueue_script( 'wp-api' );
```

Example 2 (php):
```php
wp_enqueue_script( 'my_script', 'path/to/my/script', array( 'wp-api' ) );
```

Example 3 (js):
```js
["GET", "POST", "PUT", "PATCH", "DELETE"]
```

Example 4 (js):
```js
wp.api.loadPromise.done( function() {
//... use the client here
} )
```

---

## Search Results

**URL:** https://developer.wordpress.org/rest-api/reference/search-results

**Contents:**
- Search Results
- In this article
- Schema
- List Search Results
  - Definition
  - Example Request
  - Arguments

The schema defines all the fields that exist within a search result record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer or string

JSON data type: string

JSON data type: string, Format: uri

JSON data type: string

One of: post, term, post-format

JSON data type: string

One of: post, page, category, post_tag

Query this endpoint to retrieve a collection of search results. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/search

One of: post, term, post-format

Improve it on GitHub: Search Results

See list of changes: Search Results

---

## Categories

**URL:** https://developer.wordpress.org/rest-api/reference/categories

**Contents:**
- Categories
- In this article
- Schema
- List Categories
  - Definition
  - Example Request
  - Arguments
- Create a Category
  - Arguments
  - Definition

The schema defines all the fields that exist within a category record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, embed, edit

JSON data type: integer

JSON data type: string

JSON data type: string, Format: uri

Context: view, embed, edit

JSON data type: string

Context: view, embed, edit

JSON data type: string

Context: view, embed, edit

JSON data type: string

Context: view, embed, edit

JSON data type: integer

JSON data type: object

Query this endpoint to retrieve a collection of categories. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/categories

$ curl https://example.com/wp-json/wp/v2/categories

One of: view, embed, edit

One of: id, include, name, slug, include_slugs, term_group, description, count

POST /wp/v2/categories

GET /wp/v2/categories/<id>

Query this endpoint to retrieve a specific category record.

$ curl https://example.com/wp-json/wp/v2/categories/<id>

One of: view, embed, edit

POST /wp/v2/categories/<id>

DELETE /wp/v2/categories/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/categories/<id>

Improve it on GitHub: Categories

See list of changes: Categories

---

## Global_Styles

**URL:** https://developer.wordpress.org/rest-api/reference/wp_global_styles

**Contents:**
- Global_Styles
- In this article
- Schema
- Retrieve a Global_Styles
  - Definition & Example Request
  - Arguments
- Update a Global_Styles
  - Arguments
  - Definition
  - Example Request

The schema defines all the fields that exist within a global_styles record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: embed, view, edit

JSON data type: object

JSON data type: object

JSON data type: object or string

Context: embed, view, edit

GET /wp/v2/global-styles/<id>

Query this endpoint to retrieve a specific global_styles record.

$ curl https://example.com/wp-json/wp/v2/global-styles/<id>

POST /wp/v2/global-styles/<id>

Improve it on GitHub: Global_Styles

See list of changes: Global_Styles

---

## Wp Site Health Tests

**URL:** https://developer.wordpress.org/rest-api/reference/wp-site-health-tests

**Contents:**
- Wp Site Health Tests
- In this article
- Schema
- Retrieve a Wp Site Health Test
  - Definition & Example Request
- Retrieve a Wp Site Health Test
  - Definition & Example Request
- Retrieve a Wp Site Health Test
  - Definition & Example Request
- Retrieve a Wp Site Health Test

The schema defines all the fields that exist within a wp site health test record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

JSON data type: string

JSON data type: string

One of: good, recommended, critical

JSON data type: object

JSON data type: string

JSON data type: string

GET /wp-site-health/v1/tests/background-updates

Query this endpoint to retrieve a specific wp site health test record.

$ curl https://example.com/wp-json/wp-site-health/v1/tests/background-updates

GET /wp-site-health/v1/tests/loopback-requests

Query this endpoint to retrieve a specific wp site health test record.

$ curl https://example.com/wp-json/wp-site-health/v1/tests/loopback-requests

GET /wp-site-health/v1/tests/https-status

Query this endpoint to retrieve a specific wp site health test record.

$ curl https://example.com/wp-json/wp-site-health/v1/tests/https-status

GET /wp-site-health/v1/tests/dotorg-communication

Query this endpoint to retrieve a specific wp site health test record.

$ curl https://example.com/wp-json/wp-site-health/v1/tests/dotorg-communication

GET /wp-site-health/v1/tests/authorization-header

Query this endpoint to retrieve a specific wp site health test record.

$ curl https://example.com/wp-json/wp-site-health/v1/tests/authorization-header

Improve it on GitHub: Wp Site Health Tests

See list of changes: Wp Site Health Tests

---

## Nav_Menus

**URL:** https://developer.wordpress.org/rest-api/reference/nav_menus

**Contents:**
- Nav_Menus
- In this article
- Schema
- List Nav_Menus
  - Definition
  - Example Request
  - Arguments
- Create a Nav_Menu
  - Arguments
  - Definition

The schema defines all the fields that exist within a nav_menu record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, embed, edit

JSON data type: string

JSON data type: string

Context: view, embed, edit

JSON data type: string

Context: view, embed, edit

JSON data type: object

JSON data type: array

JSON data type: boolean

Query this endpoint to retrieve a collection of nav_menus. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/menus

One of: view, embed, edit

One of: id, include, name, slug, include_slugs, term_group, description, count

GET /wp/v2/menus/<id>

Query this endpoint to retrieve a specific nav_menu record.

$ curl https://example.com/wp-json/wp/v2/menus/<id>

One of: view, embed, edit

POST /wp/v2/menus/<id>

DELETE /wp/v2/menus/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/menus/<id>

Improve it on GitHub: Nav_Menus

See list of changes: Nav_Menus

---

## Block Directory Items

**URL:** https://developer.wordpress.org/rest-api/reference/block-directory-items

**Contents:**
- Block Directory Items
- In this article
- Schema
- List Block Directory Items
  - Definition
  - Example Request
  - Arguments

The schema defines all the fields that exist within a block directory item record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

JSON data type: string

JSON data type: string

JSON data type: string

JSON data type: number

JSON data type: integer

JSON data type: integer

JSON data type: number

JSON data type: integer

JSON data type: string

JSON data type: string, Format: uri

JSON data type: string, Format: datetime (details)

JSON data type: string

Query this endpoint to retrieve a collection of block directory items. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/block-directory/search

$ curl https://example.com/wp-json/wp/v2/block-directory/search

Improve it on GitHub: Block Directory Items

See list of changes: Block Directory Items

---

## Block Revisions

**URL:** https://developer.wordpress.org/rest-api/reference/block-revisions

**Contents:**
- Block Revisions
- In this article
- Schema
- List Block Revisions
  - Definition
  - Example Request
  - Arguments
- Retrieve a Block Revision
  - Definition & Example Request
  - Arguments

The schema defines all the fields that exist within a Block Revision record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: object

JSON data type: integer

Context: view, edit, embed

JSON data type: string, Format: datetime (details)

JSON data type: string, Format: datetime (details)

JSON data type: integer

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: object

Context: view, edit, embed

JSON data type: object

Query this endpoint to retrieve a collection of Block Revisions. The response you receive can be controlled and filtered using the URL query parameters below.

GET /wp/v2/blocks/<parent>/revisions

$ curl https://example.com/wp-json/wp/v2/blocks/<parent>/revisions

One of: view, embed, edit

One of: date, id, include, relevance, slug, include_slugs, title

GET /wp/v2/blocks/<parent>/revisions/<id>

Query this endpoint to retrieve a specific Block Revision record.

$ curl https://example.com/wp-json/wp/v2/blocks/<parent>/revisions/<id>

One of: view, embed, edit

DELETE /wp/v2/blocks/<parent>/revisions/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/blocks/<parent>/revisions/<id>

GET /wp/v2/blocks/<id>/autosaves

Query this endpoint to retrieve a specific Block Revision record.

$ curl https://example.com/wp-json/wp/v2/blocks/<id>/autosaves

One of: view, embed, edit

POST /wp/v2/blocks/<id>/autosaves

GET /wp/v2/blocks/<parent>/autosaves/<id>

Query this endpoint to retrieve a specific Block Revision record.

$ curl https://example.com/wp-json/wp/v2/blocks/<parent>/autosaves/<id>

One of: view, embed, edit

Improve it on GitHub: Block Revisions

See list of changes: Block Revisions

---

## Modifying Responses

**URL:** https://developer.wordpress.org/rest-api/extending-the-rest-api/modifying-responses

**Contents:**
- Modifying Responses
- In this article
- Important Note about Changing Responses
- Using register_rest_field vs register_meta
- Adding Custom Fields to API Responses
  - Using register_rest_field
  - Examples
    - Read and write an extra field in comment responses
  - How register_rest_field Works
- Working with registered meta in the REST API

The default endpoints of the WordPress REST API are designed to return data by default that provides for the majority of sites and use cases, but there are often situations where you will need to access or expose additional data in the responses for various object types.

As with the rest of WordPress, the REST API is designed to be highly extensible to fit these needs. This guide details how to add additional data to the responses of default endpoints using the register_rest_field and register_meta functions. You can use these functions to add fields to any of the object types supported by the REST API. These custom fields can support both get and update operations.

Changing or removing data from core REST API endpoint responses can break plugins or WordPress core behavior, and should be avoided wherever possible.

The API exposes many fields on API responses, including things you might not need, or which might not fit into how your site works. While it’s tempting to modify or remove fields from REST API responses, this will cause problems with API clients that expect standard responses. This includes mobile clients, third party tools to help you manage your site, or wp-admin itself.

You may only need a small amount of data, but it’s important to keep in mind that the API is about exposing an interface to all clients, not just the feature you’re working on. Changing responses is dangerous.

Adding fields is not dangerous, so if you need to modify data, it’s much better to duplicate the field instead with your modified data. Removing fields is never encouraged; if you need to get back a smaller subset of data, use the _fields parameter or work with contexts instead.

If you must remove fields from an existing context you should ensure that the behavior is opt-in, for example by providing a custom query parameter to trigger the field removal.

The API cannot prevent you from changing responses, but the code is structured to strongly discourage doing so. Internally, field registration is powered by filters, and these can be used if you absolutely have no other choice.

There are two methods which can be used to add data to WordPress REST API responses, register_rest_field and register_meta.

register_rest_field may be used to add arbitrary fields to any REST API response, and can be used to both read and write data using the API. To register a new REST field you must provide your own callback functions to get or set the field’s value, as well as manually s

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
<?php
add_action( 'rest_api_init', function () {
    register_rest_field( 'comment', 'karma', array(
        'get_callback' => function( $comment_arr ) {
            $comment_obj = get_comment( $comment_arr['id'] );
            return (int) $comment_obj->comment_karma;
        },
        'update_callback' => function( $karma, $comment_obj ) {
            $ret = wp_update_comment( array(
                'comment_ID'    => $comment_obj->comment_ID,
                'comment_karma' => $karma
            ) );
            if ( false === $ret ) {
                return new WP_Error(
                 
...
```

Example 2 (php):
```php
<?php
// The object type. For custom post types, this is 'post';
// for custom comment types, this is 'comment'. For user meta,
// this is 'user'.
$object_type = 'post';
$meta_args = array( // Validate and sanitize the meta value.
    // Note: currently (4.7) one of 'string', 'boolean', 'integer',
    // 'number' must be used as 'type'. The default is 'string'.
    'type'         => 'string',
    // Shown in the schema for the meta key.
    'description'  => 'A meta key associated with a string meta value.',
    // Return a single value of the type.
    'single'       => true,
    // Show in t
...
```

Example 3 (php):
```php
$meta_args = array(
    'type'         => 'string',
    'description'  => 'A meta key associated with a string meta value.',
    'single'       => true,
    'show_in_rest' => true,
);
register_post_meta( 'page', 'my_meta_key', $meta_args );
```

Example 4 (json):
```json
{
  "meta": {
    "release": {
      "version": "5.2",
      "artist": "Jaco"
    }
  }
}
```

---

## Block Types

**URL:** https://developer.wordpress.org/rest-api/reference/block-types

**Contents:**
- Block Types
- In this article
- Schema
- Retrieve a Block Type
  - Definition & Example Request
  - Arguments
- Retrieve a Block Type
  - Definition & Example Request
  - Arguments
- Retrieve a Block Type

The schema defines all the fields that exist within a block type record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string

Context: embed, view, edit

JSON data type: string or null

Context: embed, view, edit

JSON data type: object or null

Context: embed, view, edit

JSON data type: object

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: object

Context: embed, view, edit

JSON data type: object

Context: embed, view, edit

JSON data type: string or null

Context: embed, view, edit

JSON data type: boolean

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: string or null

Context: embed, view, edit

JSON data type: array or null

Context: embed, view, edit

JSON data type: array or null

Context: embed, view, edit

JSON data type: array

Context: embed, view, edit

JSON data type: object or null

Context: embed, view, edit

JSON data type: string or null

Context: embed, view, edit

JSON data type: string or null

Context: embed, view, edit

JSON data type: string or null

Context: embed, view, edit

JSON data type: string or null

Context: embed, view, edit

JSON data type: string or null

Context: embed, view, edit

GET /wp/v2/block-types

Query this endpoint to retrieve a specific block type record.

$ curl https://example.com/wp-json/wp/v2/block-types

One of: view, embed, edit

GET /wp/v2/block-types/<namespace>

Query this endpoint to retrieve a specific block type record.

$ curl https://example.com/wp-json/wp/v2/block-types/<namespace>

One of: view, embed, edit

GET /wp/v2/block-types/<namespace>/<name>

Query this endpoint to retrieve a specific block type record.

$ curl https://example.com/wp-json/wp/v2/block-types/<namespace>/<name>

One of: view, embed, edit

Improve it on GitHub: Block Types

See list of changes: Block Types

---

## Authentication

**URL:** https://developer.wordpress.org/rest-api/using-the-rest-api/authentication

**Contents:**
- Authentication
- In this article
- Cookie Authentication
- Basic Authentication with Application Passwords
- Authentication Plugins

Cookie authentication is the standard authentication method included with WordPress. When you log in to your dashboard, this sets up the cookies correctly for you, so plugin and theme developers need only to have a logged-in user.

However, the REST API includes a technique called nonces to avoid CSRF issues. This prevents other sites from forcing you to perform actions without explicitly intending to do so. This requires slightly special handling for the API.

For developers using the built-in Javascript API, this is handled automatically for you. This is the recommended way to use the API for plugins and themes. Custom data models can extend wp.api.models.Base to ensure this is sent correctly for any custom requests.

For developers making manual Ajax requests, the nonce will need to be passed with each request. The API uses nonces with the action set to wp_rest. These can then be passed to the API via the _wpnonce data parameter (either POST data or in the query for GET requests), or via the X-WP-Nonce header. If no nonce is provided the API will set the current user to 0, turning the request into an unauthenticated request, even if you’re logged into WordPress.

Note: Until recently, most software had spotty support for DELETE requests. For instance, PHP doesn’t transform the request body of a DELETE request into a super global. As such, supplying the nonce as a header is the most reliable approach.

It is important to keep in mind that this authentication method relies on WordPress cookies. As a result this method is only applicable when the REST API is used inside of WordPress and the current user is logged in. In addition, the current user must have the appropriate capability to perform the action being performed.

As an example, this is how the built-in Javascript client creates the nonce:

This is then used in the base model:

Here is an example of editing the title of a post, using jQuery AJAX:

Note that you do not need to verify that the nonce is valid inside your custom end point. This is automatically done for you in rest_cookie_check_errors().

As of 5.6, WordPress has shipped with Application Passwords, which can be generated from an Edit User page (wp-admin -> Users -> Edit User).

The credentials can be passed along to REST API requests served over https:// using Basic Auth / RFC 7617 — here’s the documentation for how to use it with cURL.

For a simple command-line script example, just swap out USERNAME, PASSWORD, and HOSTNAME in this wi

*[Content truncated]*

**Examples:**

Example 1 (php):
```php
<?php
wp_localize_script( 'wp-api', 'wpApiSettings', array(
    'root' => esc_url_raw( rest_url() ),
    'nonce' => wp_create_nonce( 'wp_rest' )
) );
```

Example 2 (js):
```js
options.beforeSend = function(xhr) {
    xhr.setRequestHeader('X-WP-Nonce', wpApiSettings.nonce);

    if (beforeSend) {
        return beforeSend.apply(this, arguments);
    }
};
```

Example 3 (js):
```js
$.ajax( {
    url: wpApiSettings.root + 'wp/v2/posts/1',
    method: 'POST',
    beforeSend: function ( xhr ) {
        xhr.setRequestHeader( 'X-WP-Nonce', wpApiSettings.nonce );
    },
    data:{
        'title' : 'Hello Moon'
    }
} ).done( function ( response ) {
    console.log( response );
} );
```

Example 4 (unknown):
```unknown
curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/users?context=edit
```

---

## Block Patterns

**URL:** https://developer.wordpress.org/rest-api/reference/block-patterns

**Contents:**
- Block Patterns
- In this article
- Schema
- Retrieve a Block Pattern
  - Definition & Example Request

The schema defines all the fields that exist within a block pattern record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: number

Context: view, edit, embed

JSON data type: boolean

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: array

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

One of: core, plugin, theme, pattern-directory/core, pattern-directory/theme, pattern-directory/featured

GET /wp/v2/block-patterns/patterns

Query this endpoint to retrieve a specific block pattern record.

$ curl https://example.com/wp-json/wp/v2/block-patterns/patterns

Improve it on GitHub: Block Patterns

See list of changes: Block Patterns

---

## Application Passwords

**URL:** https://developer.wordpress.org/rest-api/reference/application-passwords

**Contents:**
- Application Passwords
- In this article
- Schema
- Retrieve a Application Password
  - Definition & Example Request
  - Arguments
- Create a Application Password
  - Arguments
  - Definition
- Delete a Application Password

The schema defines all the fields that exist within a application password record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: string, Format: uuid

Context: view, edit, embed

JSON data type: string, Format: uuid

Context: view, edit, embed

JSON data type: string

Context: view, edit, embed

JSON data type: string

JSON data type: string, Format: datetime (details)

JSON data type: string or null, Format: datetime (details)

JSON data type: string or null, Format: ip

GET /wp/v2/users/<user_id>)/application-passwords

Query this endpoint to retrieve a specific application password record.

$ curl https://example.com/wp-json/wp/v2/users/<user_id>)/application-passwords

One of: view, embed, edit

POST /wp/v2/users/<user_id>)/application-passwords

There are no arguments for this endpoint.

DELETE /wp/v2/users/<user_id>)/application-passwords

$ curl -X DELETE https://example.com/wp-json/wp/v2/users/<user_id>)/application-passwords

GET /wp/v2/users/<user_id>)/application-passwords/introspect

Query this endpoint to retrieve a specific application password record.

$ curl https://example.com/wp-json/wp/v2/users/<user_id>)/application-passwords/introspect

One of: view, embed, edit

GET /wp/v2/users/<user_id>)/application-passwords/<uuid>

Query this endpoint to retrieve a specific application password record.

$ curl https://example.com/wp-json/wp/v2/users/<user_id>)/application-passwords/<uuid>

One of: view, embed, edit

POST /wp/v2/users/<user_id>)/application-passwords/<uuid>

There are no arguments for this endpoint.

DELETE /wp/v2/users/<user_id>)/application-passwords/<uuid>

$ curl -X DELETE https://example.com/wp-json/wp/v2/users/<user_id>)/application-passwords/<uuid>

Improve it on GitHub: Application Passwords

See list of changes: Application Passwords

---

## Tags

**URL:** https://developer.wordpress.org/rest-api/reference/tags

**Contents:**
- Tags
- In this article
- Schema
- List Tags
  - Definition
  - Example Request
  - Arguments
- Create a Tag
  - Arguments
  - Definition

The schema defines all the fields that exist within a tag record. Any response from these endpoints can be expected to contain the fields below unless the `_filter` query parameter is used or the schema field only appears in a specific context.

JSON data type: integer

Context: view, embed, edit

JSON data type: integer

JSON data type: string

JSON data type: string, Format: uri

Context: view, embed, edit

JSON data type: string

Context: view, embed, edit

JSON data type: string

Context: view, embed, edit

JSON data type: string

Context: view, embed, edit

JSON data type: object

Query this endpoint to retrieve a collection of tags. The response you receive can be controlled and filtered using the URL query parameters below.

$ curl https://example.com/wp-json/wp/v2/tags

One of: view, embed, edit

One of: id, include, name, slug, include_slugs, term_group, description, count

Query this endpoint to retrieve a specific tag record.

$ curl https://example.com/wp-json/wp/v2/tags/<id>

One of: view, embed, edit

POST /wp/v2/tags/<id>

DELETE /wp/v2/tags/<id>

$ curl -X DELETE https://example.com/wp-json/wp/v2/tags/<id>

Improve it on GitHub: Tags

See list of changes: Tags

---
