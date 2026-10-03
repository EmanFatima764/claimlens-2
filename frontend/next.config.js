/** @type {import('next').NextConfig} */
module.exports = {
	reactStrictMode: true,
	webpack: (config, { dev }) => {
		if (dev) config.cache = false;
		return config;
	},
};
