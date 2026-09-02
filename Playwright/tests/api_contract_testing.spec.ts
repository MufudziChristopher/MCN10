import { test, expect } from '@playwright/test';

test('products contract expose safe, typed fields', async ({ request }) => {
	const response = await request.get('/3rdAxis/api/v1/products');
	await expect(response).toBeOK();

	const body = await response.json();
	expect(Array.isArray(body.products)).toBeTruthy();
	expect(body.products.length).toBeGreaterThan(0);

	for (const product of body.products) {
		expect(product).toMatchObject({
			id: expect.any(Number),
			name: expect.any(String), 
			stock: expect.any(Number),
		});
		expect(product.price).toMatch(/^\d+\.\d{2}$/);
		expect(product.stock).toBeGreaterThanOrEqual(0);
		expect(product).not.toHaveProperty('cost_price'); // a useful data-leak check
	}

});