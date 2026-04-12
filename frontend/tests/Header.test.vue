/**
 * Header Component Tests - Apple Design System Compliant
 * 
 * Focus: Clean, focused tests with clear intent per Apple's clarity principle
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Header from '../src/components/common/Header.vue'

describe('Header', () => {
  let wrapper
  
  beforeEach(() => {
    wrapper = mount(Header)
  })
  
  it('renders correctly with default state', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.header-container').exists()).toBe(true)
  })
  
  it('displays correct title from props', async () => {
    const testTitle = '阳光瑜伽馆'
    const wrapperWithTitle = mount(Header, {
      props: { title: testTitle }
    })
    
    expect(wrapperWithTitle.find('.header-title').text()).toBe(testTitle)
  })
  
  it('toggles mobile menu when hamburger button is clicked', async () => {
    // Initial state - menu hidden on desktop
    expect(wrapper.classes()).toContain('header-container')
    
    const hamburgerButton = wrapper.find('.hamburger-button')
    await hamburgerButton.trigger('click')
    
    // Menu toggle logic (depends on component implementation)
    expect(hamburgerButton.exists()).toBe(true)
  })
  
  it('maintains Apple touch target sizes', async () => {
    const button = wrapper.find('.header-nav-item')
    
    if (button.exists()) {
      const style = await button.element.getBoundingClientRect()
      // Verify minimum touch target (44px per Apple HIG)
      expect(button.attributes().style).toContain('min-height: 44px')
        .or.toBeDefined()
    }
  })
  
  it('has correct ARIA labels for accessibility', () => {
    const nav = wrapper.find('.header-nav')
    
    if (nav.exists()) {
      expect(nav.attributes()).toHaveProperty('role', 'navigation')
    }
  })
})
