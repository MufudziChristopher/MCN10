import { test as base, expect } from '@playwright/test';

type Fixtures = { loginPage: import('@playwright/test').Page };

export const test = base.extend<Fixtures>({
	loginPage: async ({ page }, use) => {
		await page.goto('/account/login/');
		await expect(page.getByRole('heading', { name: 'Sign in to Foxx Mart' })).toBeVisible();
		await use(page); // hand the prepared page to the test
		//optional cleanup belongs after use()
	},
});
export { expect };  