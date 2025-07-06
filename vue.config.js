module.exports = {
  publicPath: './',
  devServer: {
    proxy: {
      '/': {
        target: 'http://26.124.13.39:5000/', // URL da sua API
        changeOrigin: true,
        pathRewrite: { '^/': '' },
      },
    },
  },
}
