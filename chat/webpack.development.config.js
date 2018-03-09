const path = require('path');
const ProvidePlugin = require('webpack').ProvidePlugin;
const BundleTracker = require('webpack-bundle-tracker');


module.exports = {
    context: __dirname,
    entry: './static/js/index',

    output: {
        path: path.resolve('./static/bundles/'),
        filename: '[name]-[hash].js',
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        }),
    ],

    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {
                    presets: ['react']
                }
            },
            {
                loader: [
                    'style-loader',
                    {
                        loader: 'css-loader',
                        options: {
                            importLoader: 1,
                            modules: true,
                            camelCase: true,
                            localIdentName: '[path]___[name]__[local]___[hash:base64:5]'
                        }
                    }
                ],
                test: /\.module\.css$/,

            },
            {
                loader: [
                    'style-loader',
                    {
                        loader: 'css-loader',
                        options: {
                            importLoader: 0,
                            modules: true,
                            localIdentName: '[name]'
                        }
                    }
                ],
                test: /^((?!\.module).)*\.css$/,
            },
            {
                test: /\.(png|jpg|svg|gif)$/,
                loader: 'url-loader?limit=10000&name="[name]-[hash].[ext]"',
            },
            // {
            //     test: /\.(woff|woff2|eot|ttf|svg)$/,
            //     loader: 'file-loader?name="[name]-[hash].[ext]"',
            // },
            {
                test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                loader: "url-loader?limit=10000&mimetype=application/font-woff"
            },
            {
                test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                loader: "file-loader"
            }
        ]
    },

    resolve: {
        modules: ['node_modules'],
        extensions: ['.js', '.jsx'],
        alias: {
            GlobalStyles: path.resolve(__dirname, 'static/css'),
            Fonts: path.resolve(__dirname, 'static/webfonts')
        }
    },

    node: {
        __dirname: true
    },
};