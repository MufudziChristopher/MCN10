import { test as base, expect } from '@playwright/test';

type FreshLogin = { freshLogin: import('playwright/test').Page };

export const test = base.extend<Login>({
	freshLogin: async ({ page }, use) => {
		await page.goto('/account/register/');
		const timestamp = Date.now();
		const email = `testuser_${timestamp}@foxxmart.com`;
  		await page.goto('http://localhost:8000/account/register/');
  		await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
		await page.getByRole('textbox', { name: 'Full name' }).fill('test User');
		await page.getByRole('textbox', { name: 'Full name' }).fill('Test User');
		await page.getByRole('textbox', { name: 'Email address' }).fill(email);
		await page.getByLabel('Password', { exact: true }).fill(process.env.E2E_PASSWORD!);
		await page.getByRole('textbox', { name: 'Confirm password', exact: true }).fill(process.env.E2E_PASSWORD!);

		

		await page.getByRole('button', { name: 'Create account' }).click();
		await expect(page.getByText('FOXX MART / 01 3rd AxisAdditive manufacturing')).toBeVisible();
		await use(page); // hand the prepared page to the test

		//optional cleanup belongs after use()
	},
});
export { expect };  