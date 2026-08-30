import { test, expect } from './freshLogin';
test.describe('Testing the shopping journey', () => {
	test.beforeEach ('only adds an in-stock product to the cart', async ({ freshLogin }) => {
		await freshLogin.goto('3rdAxis/');
		await expect(freshLogin.locator('#store[aria-busy="false"]')).toBeVisible();
		await expect(freshLogin.getByTestId('cart-item-count')).toHaveText('0');

		const products = [
			'Axis Dual Drive Extruder',
			'Axis TPU Flex Lime',
			'Axis PETG Smoke Clear',
			'Axis Standard Brass Hotend',
			'Axis Hardened Steel Hotend',
			'Axis Form One',
			'Axis Forge One',
			'Axis Forge XL',
			'Axis Resin Mini',
			'Axis Resin Mini',
		];

		for (const [index, productName] of products.entries()) {
			await expect(freshLogin.locator('#store[aria-busy="false"]')).toBeVisible();
			const addToCart = freshLogin.getByRole('button', {
				name: `Add ${productName} to cart`,
			}).filter({ visible: true }).first();

			await expect(addToCart).toBeVisible();
			await addToCart.click();
			await expect(freshLogin.getByTestId('cart-item-count')).toHaveText(String(index + 1));
		}
	});

	test ('interact with the cart page', async ({ page }) => {

		await page.goto('3rdAxis/cart');
		await expect(page).toHaveURL(/\/3rdAxis\/cart\/$/);
		await expect(page.getByText('Items')).toHaveText('10 Items');


		await expect(page.getByRole('row', { name: 'View Axis Dual Drive Extruder' })).toBeVisible();
		await page.getByRole('row', { name: 'View Axis Dual Drive Extruder' }).getByLabel('Quantity').fill('2');
		await page.getByRole('row', { name: 'View Axis Dual Drive Extruder' }).getByLabel('Quantity').press('Enter');
		await expect(page.getByRole('row', { name: 'View Axis Dual Drive Extruder' }).getByLabel('Quantity')).toHaveValue('2');
		await expect(page.getByText('Items')).toHaveText('11 Items');


		await expect(page.getByRole('row', { name: 'View Axis Forge One details' })).toBeVisible();
		await page.getByRole('row', { name: 'View Axis Forge One details' }).getByLabel('Quantity').fill('2');
		await page.getByRole('row', { name: 'View Axis Forge One details' }).getByLabel('Quantity').press('Enter');
		await expect(page.getByRole('row', { name: 'View Axis Forge One details' }).getByLabel('Quantity')).toHaveValue('2');
		await expect(page.getByText('Items')).toHaveText('12 Items');


		await expect(page.getByRole('row', { name: 'View Axis PETG Smoke Clear' })).toBeVisible();
		await page.getByRole('row', { name: 'View Axis PETG Smoke Clear' }).getByLabel('Quantity').fill('0');
		await page.getByRole('row', { name: 'View Axis PETG Smoke Clear' }).getByLabel('Quantity').press('Enter');
		await expect(page.getByRole('row', { name: 'View Axis PETG Smoke Clear' })).not.toBeVisible();
		await expect(page.getByText('Items')).toHaveText('11 Items');



		await expect(page.getByRole('link', { name: 'Checkout', exact: true })).toBeVisible();
		await page.getByRole('link', { name: 'Checkout', exact: true }).click();

		await expect(page).toHaveURL(/\/checkout\//);
	});


	test ('Check out and confirm order', async ({ page }) => {
  		await page.goto('3rdAxis/checkout/');
  		await expect(page).toHaveURL('3rdAxis/checkout/')

  		await expect(page.getByText('Items10')).toBeVisible();
		await expect(page.getByText('SubtotalR173,257.00')).toBeVisible();
  		await expect(page.getByText('DeliveryR99.00')).toBeVisible();
  		await expect(page.getByText('VAT (15%)R26,003.40')).toBeVisible();
  		await expect(page.getByText('Total incl. VATR199,359.40')).toBeVisible();


		await expect(page.getByRole('textbox', { name: 'Full name' })).toHaveValue(/\S/);
  		await expect(page.getByRole('textbox', { name: 'Email address' })).toHaveValue(/\S/);
  		await expect(page.getByLabel('CountrySouth Africa')).toHaveValue('South Africa');

  		await page.getByLabel('ProvinceSelect').selectOption('Western Cape');
  		await page.getByRole('textbox', { name: 'Street address and number' }).fill('12 Long Street');
  		await page.getByRole('textbox', { name: 'Apartment, suite, building or' }).fill('Apartment 4B, The Gardens');
  		await page.getByRole('textbox', { name: 'Suburb / area' }).fill('City Bowl');
  		await page.getByRole('textbox', { name: 'City / town' }).fill('Cape Town');
  		await page.getByRole('textbox', { name: 'Postal code' }).fill('8010');
  		await page.getByRole('textbox', { name: 'Delivery instructions (' }).fill('Please leave the package at reception');
  		await page.getByRole('checkbox', { name: 'Save this address for future' }).check();
  		await page.getByRole('button', { name: 'Confirm test order →' }).click();


  		await expect(page).toHaveURL('account/?store=axis')
    	await expect(page.getByRole('region', { name: 'Invoices' })).toBeVisible();
      	await expect(page.getByText('Payment confirmed')).toBeVisible();
  		await expect(page.getByRole('link', { name: 'Download' })).toBeVisible();
  		await expect(page.getByRole('link', { name: 'View PDF' })).toBeVisible();
  		await expect(page.getByText('Request return')).toBeVisible();

  		const downloadPromise = page.waitForEvent('download');
		await page.getByRole('link', { name: 'Download' }).click();
		const download = await downloadPromise;
		expect(download.suggestedFilename()).toMatch(/\.pdf$/);
		expect(await download.failure()).toBeNull();

	})
});
