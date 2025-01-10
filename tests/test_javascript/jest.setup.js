// jest.setup.js
require('whatwg-fetch');
// require('@testing-library/jest-dom');

global.fetch = jest.fn();