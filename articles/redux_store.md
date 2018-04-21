
# Using the Redux Store Like a Database

Translations: 中文

![Your store data can be viewed from many angles by using indexes.](https://cdn-images-1.medium.com/max/2000/1*b-Rc3m2h_oQjbplfvp9s6w.gif)*Your store data can be viewed from many angles by using indexes.*

Recently I was browsing some of the Javascript discussions on the [RC](https://recurse.com) chat system, and I noticed a great question by [Kate Ray](https://twitter.com/kraykray):
> How should we structure the data in our redux store?

This is a common question when using redux, certainly one that I’ve asked myself many times. I’ve found the answer usually depends on how I plan to interact with my data.

There are a number of things to consider: am I frequently going to be iterating over the store data like a list of rows? Do I need fast O(1) access to individual items?

I’ve seen a bunch of approaches in practice, usually with some tradeoffs between access time and ease of iteration.

## Common approaches

If you’re storing some data where each item has an id, you could shape your store as an Object or as an Array of Objects.

**Array of flat objects [{values}]:
**This is the most common one by far that I’ve seen. It makes iteration easy and you can store your data in a particular order, but you cant access a specific item by id or name without iterating and filtering.

    categories: [
      {name: 'abs',  id: '32o8wafe', exercises: ['crunches', 'plank']},
      {name: 'arms', id: 'oaiwefjo', exercises: [...]},
      {name: 'legs', id: 'aoijwfeo', exercises: [...]},
    ]

**Object keyed on id {id: {values}}:
**This gives you fast O(1) access to each item, but you cant easily access the id of a given item while you’re iterating using Object.values().

    categories: {
      '32o8wafe': {name: 'abs',  exercises: ['crunches', 'plank']},
      'oaiwefjo': {name: 'arms', exercises: [...]},
      '3oij2e3c': {name: 'legs', exercises: [...]},
    }

    Object.values(categories).map(row => // cant access id here)
> **Food for thought:**
Arrays and Objects are [the same thing in JS](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array#Description).
(V8 stores them using different internal representations though)

## Structure it like a database of rows indexed by id

On our journey implementing a large redux app at [Monadical](https://monadical.com), we stumbled upon a different approach that gives us the benefit of both easy iteration with Object.values(state.categories), and fast O(1) access to individual items:

    categories: {
      '32o8wafe': {id: '32o8wafe', name: 'abs',  exercises: [...]},
      'oaiwefjo': {id: 'oaiwefjo', name: 'arms', exercises: [...]},
      '3oij2e3c': {id: '3oij2e3c', name: 'legs', exercises: [...]},
    }

Notice how the id is both the key for the row, and a property in the row itself. This little bit of duplication affords us great flexibility at access time. It’s also compatible with the [normalized](http://redux.js.org/docs/recipes/reducers/NormalizingStateShape.html) (*aka* flat) shape that the redux docs recommend.

Now you can loop over the data, and have access to the id while iterating!

Object.values(categories).map(cat => ({id: cat.id, name: cat.name}))

Or access any individual item instantly by id!

categories[‘32o8wafe’].name // 'abs'

We send our data to the frontend already shaped like this, so the frontend doesn’t need to do any processing to produce the mapping of id: values. It’s easy to do from the backend, since you’re likely pulling data out of a database where it already has an id field that you can use as a key.

## The power of indexes

The new shape we introduce above is a trivial change to make, and likely not one a team will spend much time deliberating over when designing their redux store. The real magic comes in when we access store data using different keys besides id.

Notice how the shape we introduce above is just a list of rows, with a key used to uniquely identify each row. With your store shaped like this, you can produce indexes that let you do O(1) access using any other key you desire:

**Index categories by name:**

To make the index, we write a function that takes the store data, and returns a mapping of name -> id.

    const index_by_name = (categories) =>
        Object.values(categories)
              .reduce((index, row) => {
                          index[row.name] = row.id
                          return index
                      }, {})

    // {abs: '32o8wafe', arms: 'oaiwefjo', legs: '3oij2e3c'}

![](https://cdn-images-1.medium.com/max/2572/1*y3bELbeb5YMOFNwIotJ6QQ.png)

    const ids_by_name = index_by_name(categories)

    categories[ids_by_name['abs']] // {id: '32o8wafe', name: 'abs', ...}

You can build as many indexes as you want for the same data, which gives you O(1) access based on any column, just like you’d have in a database.

If your data doesn’t change, your indexes just need to be computed once, otherwise they should be recomputed with memoized functions.
> **Food for thought:**
How can you make an index for keys that are non-unique?

![Trippy photo break. Rest your eyes for a second, then read on :)](https://cdn-images-1.medium.com/max/2000/1*z-jt1KCPbEFCaPBDOpSBrQ.gif)*Trippy photo break. Rest your eyes for a second, then read on :)*

## Sorted data

What if your categories have an inherent order (like in an array), and you need to be able to get them in order whenever iterating over your data?

You might think to do something like:

    const category_order = ['32o8wafe', 'oaiwefjo', '3oij2e3c']
    category_order.map(id => categories[id])

This is a good approach, however, it requires keeping an array separately from our data to store the order, which is suboptimal. Lets do it properly with indexes.

We send the data from our backend with an order (or idx) key specifying each row’s position, then we **make an index for order just like we would for any other key**:

    const ids_by_order =
          Object.values(categories)
                .reduce((ordered_ids, category) => {
                            ordered_ids[category.order] = category.id
                            return ordered_ids
                        }, [])

    // ['32o8wafe', 'oaiwefjo', '3oij2e3c']

Notice how this reduce operation produces an index Array instead of an Object. In JS, an array is actually just an object with the keys 0, 1, 2, …, so now we have both O(1) access to a specific id by order, and we can iterate using map, filter, and reduce on the ordered list:

    const second_category = categories[ids_by_order[1]]
    // {id: 'oaiwefjo', name: 'arms', order: '1'}

    const ordered_names = ids_by_order.map(id => categories[id].name)
    // ['abs', 'arms', 'legs']
> **Food for thought:**
Why does this work even if your order numbers [have gaps](http://www.htmlgoodies.com/beyond/javascript/dont-fear-sparse-arrays-in-javascript.html)? e.g. 0, 2, 41, 399

## Memoization

If your data never changes, you can call ids_by_key once on startup and use the produced index as a static object every time after that. However, if you’re working with changing data that will be accessed frequently, memoization is essential to avoid recalculating the index on every access (which is O(n)).

Memoized-index selectors can be accomplished with [reselect](https://github.com/reactjs/reselect), or by writing a [custom memoizer function](https://www.sitepoint.com/implementing-memoization-in-javascript/) (which is not too difficult depending on your data).

Memoized indexes mean you can call the index function on every read, instead of having to store the index in redux.

The flat data pattern with indexes that I describe above is also congruent with the pattern used by the library [Normalizr](https://github.com/paularmstrong/normalizr). If you’re into storing your data flat (separated by type), and like the index concept introduced in this article, give the [Redux Without Profanity docs](https://tonyhb.gitbooks.io/redux-without-profanity/content/normalizer.html) on Normalizr a read.
> **Food for thought:**
Memoizing using the .hash() on immutable.js objects is [**fast](https://egghead.io/lessons/javascript-lightning-fast-immutable-js-equality-checks-with-hash-codes)**.

## Higher order index functions

**All indexes are pure results of our data, **so we can also make cool higher-order index functions (*aka* functions that return functions), e.g. :

    const ids_by_key = (key) => (data) =>  // make index(data) for key
          Object.values(data)
                .reduce((index, row) => {
                            index[row[key]] = row.id
                            return index
                        }, {})

    const ids_by_name = ids_by_key('name')  // returns an index function
    const abs_id = ids_by_name(categories)['abs']
    // '32o8wafe'
> **Food for thought:**
Write an index maker function that makes indexes keyed on a tuple of two keys: `${row[key1]}-${row[key2]}` -> id

## Why does any of this matter?
> React and Flux/Redux solved […] rendering and state management. It became possible now to build truly advanced web apps, focusing on actual domain, instead of struggling with underlying implementation.
> The problem however is that systems keeps growing. We are building more UIs and loading and transforming even more data…

— Roman Liutikov: [On Web Apps and Databases](https://medium.com/@roman01la/on-web-apps-and-databases-c026f77b93f4)

As frontends start to approach the complexity of backends, we end up manually reimplementing things that have already existed for decades in the backend: databases, message queues, and other stereotypically server-only infrastructure. Many of the frontend patterns that are considered modern— like functional reactive programming — have been around [since Windows 3.1](https://tomjoro.github.io/2017-02-03-why-reactive-fp-sucks/).

State management lessons that we’ve already learned from SQL databases in the 90’s can be applied to our frontend to help us maintain the clarity, elegance, and consistency of our data. Using indexes to avoid duplication and jump to specific parts of a a central, consistent data set is one such example, and I’m sure there are many more that I have yet to discover.

## Further reading

If you want more database-like features in the browser, check out: [redux-orm](https://github.com/tommikaikkonen/redux-orm), [IndexedDB](https://developer.mozilla.org/en-US/docs/Glossary/IndexedDB) (the replacement to Web SQL), and [GraphQL](http://graphql.org/). Remember though, don’t start installing libraries until you know exactly why you need them.

* [http://redux.js.org/docs/basics/Reducers.html#designing-the-state-shape](http://redux.js.org/docs/basics/Reducers.html#designing-the-state-shape)

* [http://redux.js.org/docs/recipes/reducers/NormalizingStateShape.html](http://redux.js.org/docs/recipes/reducers/NormalizingStateShape.html)

* [https://egghead.io/lessons/javascript-redux-normalizing-the-state-shape](https://egghead.io/lessons/javascript-redux-normalizing-the-state-shape)

* [https://stackoverflow.com/questions/33940015/how-to-choose-the-redux-state-shape-for-an-app-with-list-detail-views-and-pagina](https://stackoverflow.com/questions/33940015/how-to-choose-the-redux-state-shape-for-an-app-with-list-detail-views-and-pagina)

* [https://stackoverflow.com/questions/34995822/how-to-get-best-practice-react-redux-nested-array-data](https://stackoverflow.com/questions/34995822/how-to-get-best-practice-react-redux-nested-array-data?noredirect=1&lq=1)

* [https://codeburst.io/how-to-store-your-state-data-f17ceca37aa](https://codeburst.io/how-to-store-your-state-data-f17ceca37aa)

* [https://tonyhb.gitbooks.io/redux-without-profanity/content/normalizer.html](https://tonyhb.gitbooks.io/redux-without-profanity/content/normalizer.html)

* [https://github.com/tommikaikkonen/redux-orm](https://github.com/tommikaikkonen/redux-orm)

—
> **tl;dr**
- Store your redux data in normalized form {id: {id, attr1, attr2, attr3}}
- Make{attr: id} indexes for fast O(1) access by other keys e.g. ids_by_name
- Iterate sorted data using an Array index *ids_by_order.map(id => data[id])
- *Use pure index functions and memoize them if your data changes frequently

## —

Hopefully you find this useful! If so, give this article a 💚, or ping me on twitter [@theSquashSH](https://twitter.com/theSquashSH).

If you’re interested in working on cool Django + React/Redux projects involving Ethereum, [Monadical is hiring](https://monadical.com) remote & local devs (we’ll fly you to sunny Medellín for the first month)!

![](https://cdn-images-1.medium.com/max/3796/1*uRMpX-1G6q12KDu23mGcvQ.png)
